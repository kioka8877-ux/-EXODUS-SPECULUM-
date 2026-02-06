#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate ALCHIMISTE - Chunk Processor
Traitement par chunks pour éviter saturation Drive (15GB limit Colab).

Workflow streaming anti-goulot:
1. Render chunk de N frames
2. ESRGAN upscale chunk
3. RIFE interpolate chunk
4. Encoder chunk en vidéo temp
5. Supprimer frames temporaires
6. Répéter pour chunk suivant
7. Concaténer vidéos temp

Philosophie: Diviser pour régner - transmuter par petits lots.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cycles_renderer import CyclesRenderer
    from .esrgan_upscaler import ESRGANUpscaler
    from .rife_interpolator import RIFEInterpolator

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None

CHUNK_SIZE_FRAMES = 120
CLEANUP_TEMP_FILES = True
FFMPEG_PRESET = "fast"
FFMPEG_CRF = 18


class ChunkProcessor:
    """
    Traitement par chunks pour éviter saturation Drive (15GB limit Colab).
    
    Chaque chunk est traité complètement (render → upscale → interpolate → encode)
    avant de passer au suivant, permettant de libérer l'espace disque.
    
    Pipeline par chunk:
    1. Render N frames (Cycles)
    2. ESRGAN x4 (si activé)
    3. RIFE interpolation (si activé)
    4. Encode en vidéo MP4
    5. Cleanup frames temporaires
    6. Répéter jusqu'à fin d'animation
    7. Concaténer tous les chunks
    
    Usage:
        processor = ChunkProcessor(chunk_size=120, cleanup=True)
        result = processor.process_in_chunks(
            scene_path,
            output_dir,
            renderer,
            upscaler,
            interpolator
        )
    """
    
    def __init__(
        self, 
        chunk_size: int = CHUNK_SIZE_FRAMES,
        cleanup: bool = CLEANUP_TEMP_FILES,
        verbose: bool = True
    ):
        """
        Args:
            chunk_size: Nombre de frames par chunk
            cleanup: Supprime les fichiers temporaires après traitement
            verbose: Affiche les logs
        """
        self.chunk_size = chunk_size
        self.cleanup = cleanup
        self.verbose = verbose
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"📦 [ChunkProcessor] {message}")
    
    def _encode_chunk(
        self, 
        frames_dir: str, 
        output_path: str, 
        fps: int = 60,
        frame_pattern: str = "frame_%04d.png"
    ) -> str:
        """
        Encode un chunk de frames en vidéo MP4.
        
        Args:
            frames_dir: Dossier contenant les frames
            output_path: Chemin de sortie de la vidéo
            fps: FPS de la vidéo
            frame_pattern: Pattern des noms de fichiers
            
        Returns:
            Chemin de la vidéo encodée
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        frames = sorted(Path(frames_dir).glob("*.png"))
        if not frames:
            raise ValueError(f"Aucune frame dans {frames_dir}")
        
        first_frame = frames[0]
        frame_pattern = self._detect_frame_pattern(frames_dir)
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", f"{frames_dir}/{frame_pattern}",
            "-c:v", "libx264",
            "-preset", FFMPEG_PRESET,
            "-crf", str(FFMPEG_CRF),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            self._log(f"  ✓ Chunk encodé: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            self._log(f"  ❌ Encodage failed: {e.stderr[:200]}")
            raise RuntimeError(f"FFmpeg failed: {e.stderr}")
    
    def _detect_frame_pattern(self, frames_dir: str) -> str:
        """
        Détecte le pattern de nommage des frames.
        
        Args:
            frames_dir: Dossier des frames
            
        Returns:
            Pattern FFmpeg (ex: frame_%04d.png)
        """
        frames = sorted(Path(frames_dir).glob("*.png"))
        if not frames:
            return "frame_%04d.png"
        
        first_name = frames[0].stem
        
        import re
        match = re.search(r'(\d+)$', first_name)
        if match:
            digits = len(match.group(1))
            prefix = first_name[:match.start()]
            return f"{prefix}%0{digits}d.png"
        
        return "frame_%04d.png"
    
    def _concatenate_videos(
        self, 
        video_list: List[str], 
        output_path: str
    ) -> str:
        """
        Concatène plusieurs vidéos en une seule.
        
        Args:
            video_list: Liste des chemins des vidéos
            output_path: Chemin de la vidéo finale
            
        Returns:
            Chemin de la vidéo concaténée
        """
        if len(video_list) == 1:
            shutil.copy2(video_list[0], output_path)
            self._log(f"✓ Vidéo unique copiée: {output_path}")
            return output_path
        
        list_file = f"{Path(output_path).parent}/concat_list.txt"
        
        with open(list_file, 'w') as f:
            for video in video_list:
                f.write(f"file '{video}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            os.remove(list_file)
            
            self._log(f"✓ Vidéos concaténées: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Concaténation failed: {e.stderr[:200]}")
            raise RuntimeError(f"FFmpeg concat failed: {e.stderr}")
    
    def _cleanup_directory(self, dir_path: str) -> None:
        """
        Supprime un dossier et son contenu.
        
        Args:
            dir_path: Chemin du dossier à supprimer
        """
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
            self._log(f"  🗑️ Cleanup: {dir_path}")
    
    def process_in_chunks(
        self,
        scene_path: str,
        output_dir: str,
        renderer: "CyclesRenderer",
        upscaler: Optional["ESRGANUpscaler"] = None,
        interpolator: Optional["RIFEInterpolator"] = None,
        final_fps: int = 60
    ) -> Dict[str, Any]:
        """
        Process l'animation par chunks avec cleanup automatique.
        
        Args:
            scene_path: Chemin du fichier .blend
            output_dir: Dossier de sortie
            renderer: Instance CyclesRenderer configurée
            upscaler: Instance ESRGANUpscaler (optionnel)
            interpolator: Instance RIFEInterpolator (optionnel)
            final_fps: FPS de la vidéo finale
            
        Returns:
            Dict avec les résultats du traitement
        """
        start_time = time.time()
        
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - traitement simulé")
            return self._simulate_processing(output_dir)
        
        bpy.ops.wm.open_mainfile(filepath=scene_path)
        scene = bpy.context.scene
        
        frame_start = scene.frame_start
        frame_end = scene.frame_end
        total_frames = frame_end - frame_start + 1
        
        self._log(f"Animation: frames {frame_start}-{frame_end} ({total_frames} frames)")
        self._log(f"Chunks de {self.chunk_size} frames")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        chunk_videos = []
        chunk_id = 0
        
        for chunk_start in range(frame_start, frame_end + 1, self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size - 1, frame_end)
            chunk_frames = chunk_end - chunk_start + 1
            
            self._log(f"\n{'='*50}")
            self._log(f"CHUNK {chunk_id}: frames {chunk_start}-{chunk_end} ({chunk_frames} frames)")
            self._log(f"{'='*50}")
            
            chunk_raw = str(output_path / f"temp_chunk_{chunk_id:03d}_raw")
            chunk_4x = str(output_path / f"temp_chunk_{chunk_id:03d}_4x")
            chunk_interp = str(output_path / f"temp_chunk_{chunk_id:03d}_interp")
            
            self._log(f"  1/4 Rendu Cycles...")
            renderer.render_frame_range(chunk_raw, chunk_start, chunk_end)
            current_frames_dir = chunk_raw
            current_fps = renderer.config['fps']
            
            if upscaler:
                self._log(f"  2/4 ESRGAN x4...")
                upscaler.upscale_frames(current_frames_dir, chunk_4x)
                
                if self.cleanup:
                    self._cleanup_directory(current_frames_dir)
                current_frames_dir = chunk_4x
            else:
                self._log(f"  2/4 ESRGAN: skip")
            
            if interpolator:
                self._log(f"  3/4 RIFE interpolation...")
                multiplier = final_fps / current_fps
                interpolator.interpolate_frames(
                    current_frames_dir, 
                    chunk_interp,
                    multiplier=multiplier
                )
                
                if self.cleanup and current_frames_dir != chunk_raw:
                    self._cleanup_directory(current_frames_dir)
                current_frames_dir = chunk_interp
            else:
                self._log(f"  3/4 RIFE: skip")
            
            self._log(f"  4/4 Encodage MP4...")
            chunk_video = str(output_path / f"chunk_{chunk_id:03d}.mp4")
            self._encode_chunk(current_frames_dir, chunk_video, fps=final_fps)
            chunk_videos.append(chunk_video)
            
            if self.cleanup:
                self._cleanup_directory(current_frames_dir)
            
            chunk_id += 1
        
        self._log(f"\n{'='*50}")
        self._log(f"FINALISATION: Concaténation de {len(chunk_videos)} chunks")
        self._log(f"{'='*50}")
        
        final_video = str(output_path / "temp_render.mp4")
        self._concatenate_videos(chunk_videos, final_video)
        
        if self.cleanup:
            for cv in chunk_videos:
                if Path(cv).exists():
                    os.remove(cv)
                    self._log(f"  🗑️ Cleanup chunk: {cv}")
        
        total_time = time.time() - start_time
        
        self._log(f"\n✓ Traitement terminé en {total_time:.1f}s")
        
        return {
            "status": "success",
            "final_video": final_video,
            "total_frames": total_frames,
            "chunks_processed": chunk_id,
            "chunk_size": self.chunk_size,
            "final_fps": final_fps,
            "processing_time_seconds": total_time,
            "cleanup_enabled": self.cleanup
        }
    
    def _simulate_processing(self, output_dir: str) -> Dict[str, Any]:
        """
        Simule le traitement quand bpy n'est pas disponible.
        
        Args:
            output_dir: Dossier de sortie
            
        Returns:
            Dict avec les résultats simulés
        """
        return {
            "status": "simulated",
            "final_video": f"{output_dir}/temp_render.mp4",
            "total_frames": 100,
            "chunks_processed": 1,
            "chunk_size": self.chunk_size,
            "final_fps": 60,
            "processing_time_seconds": 0.0,
            "cleanup_enabled": self.cleanup
        }
    
    def estimate_disk_usage(
        self,
        total_frames: int,
        resolution: tuple,
        upscale: bool = True,
        interpolate: bool = True
    ) -> Dict[str, float]:
        """
        Estime l'utilisation disque par chunk.
        
        Args:
            total_frames: Nombre total de frames
            resolution: Résolution de rendu
            upscale: ESRGAN activé
            interpolate: RIFE activé
            
        Returns:
            Dict avec les estimations en GB
        """
        width, height = resolution
        
        bytes_per_pixel = 6
        frame_size_bytes = width * height * bytes_per_pixel
        frame_size_mb = frame_size_bytes / (1024 * 1024)
        
        chunk_raw_mb = self.chunk_size * frame_size_mb
        
        if upscale:
            upscaled_res = (width * 4, height * 4)
            upscaled_frame_bytes = upscaled_res[0] * upscaled_res[1] * bytes_per_pixel
            chunk_4x_mb = self.chunk_size * upscaled_frame_bytes / (1024 * 1024)
        else:
            chunk_4x_mb = 0
        
        if interpolate:
            multiplier = 2.5
            if upscale:
                chunk_interp_mb = chunk_4x_mb * multiplier
            else:
                chunk_interp_mb = chunk_raw_mb * multiplier
        else:
            chunk_interp_mb = 0
        
        if self.cleanup:
            peak_mb = max(chunk_raw_mb, chunk_4x_mb, chunk_interp_mb)
        else:
            peak_mb = chunk_raw_mb + chunk_4x_mb + chunk_interp_mb
        
        num_chunks = (total_frames + self.chunk_size - 1) // self.chunk_size
        video_chunk_mb = 50
        total_video_mb = num_chunks * video_chunk_mb
        
        return {
            "frame_size_mb": round(frame_size_mb, 2),
            "chunk_raw_mb": round(chunk_raw_mb, 2),
            "chunk_4x_mb": round(chunk_4x_mb, 2),
            "chunk_interp_mb": round(chunk_interp_mb, 2),
            "peak_disk_mb": round(peak_mb, 2),
            "peak_disk_gb": round(peak_mb / 1024, 2),
            "total_video_mb": round(total_video_mb, 2),
            "num_chunks": num_chunks
        }


if __name__ == "__main__":
    print("=" * 60)
    print("📦 CHUNK PROCESSOR - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   CHUNK_SIZE_FRAMES: {CHUNK_SIZE_FRAMES}")
    print(f"   CLEANUP_TEMP_FILES: {CLEANUP_TEMP_FILES}")
    print(f"   FFMPEG_PRESET: {FFMPEG_PRESET}")
    print(f"   FFMPEG_CRF: {FFMPEG_CRF}")
    print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
    
    processor = ChunkProcessor(verbose=True)
    
    print(f"\n📊 Estimation disque (720 frames, 1080p, upscale+interp):")
    estimate = processor.estimate_disk_usage(
        total_frames=720,
        resolution=(1920, 1080),
        upscale=True,
        interpolate=True
    )
    for key, value in estimate.items():
        print(f"   {key}: {value}")
    
    print(f"\n📊 Estimation disque (sans cleanup):")
    processor_no_cleanup = ChunkProcessor(cleanup=False)
    estimate_no_cleanup = processor_no_cleanup.estimate_disk_usage(
        total_frames=720,
        resolution=(1920, 1080),
        upscale=True,
        interpolate=True
    )
    print(f"   peak_disk_gb: {estimate_no_cleanup['peak_disk_gb']}")
    
    print("\n✅ Module chunk_processor.py fonctionnel")
