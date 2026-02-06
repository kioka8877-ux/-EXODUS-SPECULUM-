#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate ALCHIMISTE - Pipeline Orchestrateur
Pipeline complet de transmutation: Rendu brut → 4K/60FPS.

Input: scene_animated.blend (depuis F06) + TURBO_MODE configuration
Output: Frames finales + temp_render.mp4 dans FRIGATE_07_ALCHIMISTE/OUTPUT/

Protocole TURBO-SPECULUM:
- ÉCLAIREUR: Rendu direct 540p/12fps (preview rapide)
- CONQUÉRANT: 1080p/24fps → ESRGAN 4x → RIFE 2.5x → 4K/60fps
- SOUVERAIN: Rendu natif 4K/60fps (compute heavy)

Philosophie: Du Plomb à l'Or
Transformer le rendu brut en vidéo cristalline via l'alchimie du machine learning.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.config.paths import (
        F06_OUTPUT, F07_OUTPUT, PathConfig
    )
except ImportError:
    F06_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_06_DIRECTOR/OUTPUT/"
    F07_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_07_ALCHIMISTE/OUTPUT/"
    PathConfig = None

from .cycles_renderer import CyclesRenderer, TURBO_MODES
from .esrgan_upscaler import ESRGANUpscaler
from .rife_interpolator import RIFEInterpolator
from .chunk_processor import ChunkProcessor, CHUNK_SIZE_FRAMES, CLEANUP_TEMP_FILES

EXODUS_VERSION = "0.7.0"


class AlchimistePipeline:
    """
    Pipeline complet de transmutation: Rendu brut → 4K/60FPS.
    
    Protocole TURBO-SPECULUM:
    - ÉCLAIREUR: Rendu direct 540p/12fps (preview)
    - CONQUÉRANT: 1080p/24fps → ESRGAN 4x → RIFE 2.5x → 4K/60fps
    - SOUVERAIN: Rendu natif 4K/60fps (compute heavy)
    
    Le mode CONQUÉRANT est l'alchimie optimale: qualité maximale avec VRAM minimale.
    Render low-res → ESRGAN 4x → RIFE interpolation = 4K/60FPS sans la VRAM d'un rendu natif.
    
    Usage:
        pipeline = AlchimistePipeline(project_id="mon_projet", turbo_mode="conquerant")
        result = pipeline.run(scene_path="/path/to/scene_animated.blend")
    """
    
    def __init__(
        self, 
        project_id: str, 
        turbo_mode: str = "conquerant",
        verbose: bool = True
    ):
        """
        Args:
            project_id: Identifiant unique du projet
            turbo_mode: Mode TURBO-SPECULUM (eclaireur/conquerant/souverain)
            verbose: Affiche les logs détaillés
        """
        if turbo_mode not in TURBO_MODES:
            raise ValueError(f"Mode inconnu: {turbo_mode}. Valides: {list(TURBO_MODES.keys())}")
        
        self.project_id = project_id
        self.turbo_mode = turbo_mode
        self.config = TURBO_MODES[turbo_mode]
        self.verbose = verbose
        
        self.renderer = CyclesRenderer(turbo_mode=turbo_mode, verbose=verbose)
        
        if self.config['upscale_chain']:
            self.upscaler = ESRGANUpscaler(verbose=verbose)
            self.interpolator = RIFEInterpolator(verbose=verbose)
        else:
            self.upscaler = None
            self.interpolator = None
        
        self.chunk_processor = ChunkProcessor(
            chunk_size=CHUNK_SIZE_FRAMES,
            cleanup=CLEANUP_TEMP_FILES,
            verbose=verbose
        )
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(message)
    
    def _print_banner(self) -> None:
        """Affiche la bannière de la frégate."""
        self._log("\n" + "=" * 60)
        self._log("⚗️  FRÉGATE ALCHIMISTE - TRANSMUTATION")
        self._log(f"   Mode: {self.turbo_mode.upper()}")
        self._log(f"   Version: {EXODUS_VERSION}")
        self._log("=" * 60)
    
    def _print_config(self) -> None:
        """Affiche la configuration active."""
        self._log(f"\n📋 Configuration TURBO-SPECULUM:")
        self._log(f"   Render: {self.config['render_resolution'][0]}x{self.config['render_resolution'][1]}")
        self._log(f"   Samples: {self.config['samples']}")
        self._log(f"   FPS source: {self.config['fps']}")
        self._log(f"   Denoiser: {self.config['denoiser']}")
        
        if self.config['upscale_chain']:
            self._log(f"   Upscale chain: {' → '.join(self.config['upscale_chain'])}")
            self._log(f"   Final: {self.config['final_resolution'][0]}x{self.config['final_resolution'][1]} @ {self.config['final_fps']}fps")
        else:
            self._log(f"   Upscale: Désactivé (rendu direct)")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Vérifie les dépendances externes.
        
        Returns:
            Dict avec le status de chaque dépendance
        """
        deps = {
            "bpy": BPY_AVAILABLE,
            "ffmpeg": self._check_ffmpeg()
        }
        
        if self.upscaler:
            deps["esrgan"] = self.upscaler.check_installation()
        if self.interpolator:
            deps["rife"] = self.interpolator.check_installation()
        
        self._log("\n🔧 Dépendances:")
        for dep, status in deps.items():
            icon = "✓" if status else "✗"
            self._log(f"   {icon} {dep}")
        
        return deps
    
    def _check_ffmpeg(self) -> bool:
        """Vérifie que FFmpeg est installé."""
        import shutil
        return shutil.which("ffmpeg") is not None
    
    def run(
        self,
        scene_animated_path: Optional[str] = None,
        output_path: Optional[str] = None,
        use_chunking: bool = True,
        skip_dependency_check: bool = False
    ) -> Dict[str, Any]:
        """
        Pipeline complet F07:
        1. Charger scene_animated.blend
        2. Configurer Cycles selon TURBO_MODE
        3. Si chunking: process par chunks avec cleanup
        4. Sinon: render complet puis upscale
        5. Sauvegarder temp_render.mp4
        
        Args:
            scene_animated_path: Chemin du .blend (défaut: F06_OUTPUT)
            output_path: Dossier de sortie (défaut: F07_OUTPUT/project_id/)
            use_chunking: Utilise le traitement par chunks
            skip_dependency_check: Ignore la vérification des dépendances
            
        Returns:
            Dict avec les résultats du pipeline
        """
        start_time = time.time()
        
        self._print_banner()
        self._print_config()
        
        if scene_animated_path is None:
            scene_animated_path = f"{F06_OUTPUT}scene_animated.blend"
        
        if output_path is None:
            output_dir = Path(F07_OUTPUT) / self.project_id
        else:
            output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self._log(f"\n📂 Chemins:")
        self._log(f"   Input: {scene_animated_path}")
        self._log(f"   Output: {output_dir}")
        
        if not skip_dependency_check:
            deps = self.check_dependencies()
            if not deps.get("bpy", False):
                self._log("\n⚠️ bpy non disponible - mode simulation")
        
        result = {}
        
        if use_chunking and self.config['upscale_chain']:
            self._log("\n🔄 Mode: Chunking avec upscale chain")
            result = self.chunk_processor.process_in_chunks(
                scene_path=scene_animated_path,
                output_dir=str(output_dir),
                renderer=self.renderer,
                upscaler=self.upscaler,
                interpolator=self.interpolator,
                final_fps=self.config['final_fps']
            )
        else:
            self._log("\n🔄 Mode: Rendu direct (sans chunking)")
            result = self._run_direct_render(
                scene_path=scene_animated_path,
                output_dir=str(output_dir)
            )
        
        total_time = time.time() - start_time
        
        manifest = self._create_manifest(result, total_time, output_dir)
        manifest_path = output_dir / "alchimiste_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        self._print_summary(result, total_time)
        
        return {
            "status": "success",
            "project_id": self.project_id,
            "turbo_mode": self.turbo_mode,
            "output_dir": str(output_dir),
            "manifest_path": str(manifest_path),
            "processing_time_seconds": total_time,
            **result
        }
    
    def _run_direct_render(
        self, 
        scene_path: str, 
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Rendu direct sans chunking (ÉCLAIREUR ou SOUVERAIN).
        
        Args:
            scene_path: Chemin du .blend
            output_dir: Dossier de sortie
            
        Returns:
            Dict avec les résultats
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - rendu simulé")
            return {
                "status": "simulated",
                "frames_dir": f"{output_dir}/frames_raw",
                "frame_count": 100,
                "resolution": self.config['render_resolution'],
                "fps": self.config['fps']
            }
        
        bpy.ops.wm.open_mainfile(filepath=scene_path)
        
        self.renderer.configure_cycles()
        
        frames_dir = f"{output_dir}/frames_raw"
        render_result = self.renderer.render_animation(frames_dir)
        
        final_video = f"{output_dir}/temp_render.mp4"
        self._encode_final_video(frames_dir, final_video, self.config['fps'])
        
        return {
            "status": "success",
            "final_video": final_video,
            "frames_dir": frames_dir,
            **render_result
        }
    
    def _encode_final_video(
        self, 
        frames_dir: str, 
        output_path: str, 
        fps: int
    ) -> str:
        """
        Encode les frames en vidéo finale.
        
        Args:
            frames_dir: Dossier des frames
            output_path: Chemin de sortie
            fps: FPS de la vidéo
            
        Returns:
            Chemin de la vidéo
        """
        import subprocess
        
        frame_pattern = "frame_%04d.png"
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", f"{frames_dir}/{frame_pattern}",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        self._log(f"✓ Vidéo finale: {output_path}")
        
        return output_path
    
    def _create_manifest(
        self, 
        result: Dict[str, Any], 
        total_time: float,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Crée le manifest JSON du traitement.
        
        Args:
            result: Résultats du pipeline
            total_time: Temps total de traitement
            output_dir: Dossier de sortie
            
        Returns:
            Dict manifest
        """
        return {
            "exodus_version": EXODUS_VERSION,
            "frigate": "F07_ALCHIMISTE",
            "project_id": self.project_id,
            "timestamp": datetime.now().isoformat(),
            "turbo_mode": self.turbo_mode,
            "config": {
                "render_resolution": self.config['render_resolution'],
                "final_resolution": self.config['final_resolution'],
                "samples": self.config['samples'],
                "source_fps": self.config['fps'],
                "final_fps": self.config['final_fps'],
                "denoiser": self.config['denoiser'],
                "upscale_chain": self.config['upscale_chain']
            },
            "output": {
                "directory": str(output_dir),
                "video": result.get('final_video'),
                "frames_dir": result.get('frames_dir'),
                "frame_count": result.get('frame_count') or result.get('total_frames')
            },
            "processing": {
                "time_seconds": total_time,
                "chunks_processed": result.get('chunks_processed'),
                "status": result.get('status')
            }
        }
    
    def _print_summary(self, result: Dict[str, Any], total_time: float) -> None:
        """Affiche le résumé du traitement."""
        self._log("\n" + "=" * 60)
        self._log("⚗️  TRANSMUTATION TERMINÉE")
        self._log("=" * 60)
        self._log(f"   Status: {result.get('status', 'unknown')}")
        self._log(f"   Temps total: {total_time:.1f}s ({total_time/60:.1f} min)")
        
        if result.get('final_video'):
            self._log(f"   Vidéo: {result['final_video']}")
        
        if result.get('total_frames') or result.get('frame_count'):
            frames = result.get('total_frames') or result.get('frame_count')
            fps = total_time / frames if frames > 0 else 0
            self._log(f"   Frames: {frames} ({fps:.2f}s/frame)")
        
        self._log(f"   Résolution finale: {self.config['final_resolution'][0]}x{self.config['final_resolution'][1]}")
        self._log(f"   FPS final: {self.config['final_fps']}")


def run_alchimiste_pipeline(
    scene_animated_path: Optional[str] = None,
    output_path: Optional[str] = None,
    project_id: str = "default",
    turbo_mode: str = "conquerant",
    use_chunking: bool = True
) -> Dict[str, Any]:
    """
    Fonction helper pour exécuter le pipeline Alchimiste.
    
    Args:
        scene_animated_path: Chemin du .blend (défaut: F06_OUTPUT)
        output_path: Dossier de sortie (défaut: F07_OUTPUT)
        project_id: Identifiant du projet
        turbo_mode: Mode TURBO-SPECULUM
        use_chunking: Active le traitement par chunks
        
    Returns:
        Dict avec les résultats du pipeline
    """
    pipeline = AlchimistePipeline(
        project_id=project_id,
        turbo_mode=turbo_mode
    )
    
    return pipeline.run(
        scene_animated_path=scene_animated_path,
        output_path=output_path,
        use_chunking=use_chunking
    )


if __name__ == "__main__":
    print("=" * 60)
    print("⚗️ ALCHIMISTE PIPELINE - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   EXODUS_VERSION: {EXODUS_VERSION}")
    print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
    print(f"   F06_OUTPUT: {F06_OUTPUT}")
    print(f"   F07_OUTPUT: {F07_OUTPUT}")
    
    print(f"\n📋 TURBO_MODES:")
    for mode, config in TURBO_MODES.items():
        print(f"\n   {mode.upper()}:")
        print(f"      Render: {config['render_resolution']}")
        print(f"      Final: {config['final_resolution']} @ {config['final_fps']}fps")
        print(f"      Upscale: {config['upscale_chain']}")
    
    print(f"\n🔧 Test instanciation:")
    for mode in TURBO_MODES.keys():
        pipeline = AlchimistePipeline(
            project_id="test_project",
            turbo_mode=mode,
            verbose=False
        )
        print(f"   ✓ Mode {mode}: renderer={pipeline.renderer is not None}, upscaler={pipeline.upscaler is not None}")
    
    if len(sys.argv) > 1:
        scene_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        mode = sys.argv[3] if len(sys.argv) > 3 else "conquerant"
        
        print(f"\n🚀 Exécution pipeline:")
        result = run_alchimiste_pipeline(
            scene_animated_path=scene_path,
            output_path=output_dir,
            project_id="cli_run",
            turbo_mode=mode
        )
        print(json.dumps(result, indent=2, default=str))
    else:
        print("\n📖 Usage:")
        print("   python alchimiste_pipeline.py <scene.blend> [output_dir] [turbo_mode]")
        print("   Modes: eclaireur, conquerant, souverain")
    
    print("\n✅ Module alchimiste_pipeline.py fonctionnel")
