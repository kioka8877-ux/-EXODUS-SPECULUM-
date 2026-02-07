#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCANNER - Extracteur de Frames
F01-001 à F01-003

Extrait les frames d'une vidéo source via FFmpeg.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
import time


class FrameExtractor:
    """
    Extracteur de frames vidéo via FFmpeg.
    
    Supporte: MP4, MOV, AVI, MKV, WEBM
    Output: PNG (lossless)
    """
    
    SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    
    def __init__(self, output_dir: str, fps: float = 2.0):
        """
        Args:
            output_dir: Dossier de sortie pour les frames
            fps: Frames par seconde à extraire (défaut: 2 fps)
        """
        self.output_dir = Path(output_dir)
        self.fps = fps
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Valide et analyse la vidéo source.
        
        Returns:
            Dict avec: duration, width, height, fps, format
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Vidéo non trouvée: {video_path}")
            
        ext = video_path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Format non supporté: {ext}. Supportés: {self.SUPPORTED_FORMATS}")
        
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams', '-show_format',
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe erreur: {result.stderr}")
            
        data = json.loads(result.stdout)
        
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
                
        if not video_stream:
            raise ValueError("Aucun stream vidéo trouvé")
            
        fps_str = video_stream.get('r_frame_rate', '30/1')
        if '/' in fps_str:
            num, den = map(int, fps_str.split('/'))
            source_fps = num / den if den else 30
        else:
            source_fps = float(fps_str)
            
        return {
            'path': str(video_path),
            'filename': video_path.name,
            'format': ext,
            'duration': float(data['format'].get('duration', 0)),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'source_fps': source_fps,
            'extraction_fps': self.fps,
            'estimated_frames': int(float(data['format'].get('duration', 0)) * self.fps)
        }
    
    def extract_frames(self, video_path: str, 
                       start_time: Optional[float] = None,
                       duration: Optional[float] = None) -> Dict[str, Any]:
        """
        Extrait les frames de la vidéo.
        
        Args:
            video_path: Chemin vers la vidéo
            start_time: Temps de début (secondes)
            duration: Durée à extraire (secondes)
            
        Returns:
            Dict avec: frame_count, output_dir, frames_list
        """
        video_info = self.validate_video(video_path)
        
        print(f"📹 Extraction frames: {video_info['filename']}")
        print(f"   Résolution: {video_info['width']}x{video_info['height']}")
        print(f"   Durée: {video_info['duration']:.1f}s")
        print(f"   FPS extraction: {self.fps}")
        print(f"   Frames estimées: {video_info['estimated_frames']}")
        
        frames_dir = self.output_dir / 'frames'
        frames_dir.mkdir(exist_ok=True)
        
        output_pattern = str(frames_dir / 'frame_%04d.png')
        
        cmd = ['ffmpeg', '-y', '-i', str(video_path)]
        
        if start_time is not None:
            cmd.extend(['-ss', str(start_time)])
        if duration is not None:
            cmd.extend(['-t', str(duration)])
            
        cmd.extend([
            '-vf', f'fps={self.fps}',
            '-pix_fmt', 'rgb24',
            output_pattern
        ])
        
        print(f"   Commande: {' '.join(cmd)}")
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg erreur: {result.stderr}")
            
        frames = sorted(frames_dir.glob('frame_*.png'))
        
        print(f"✅ Extraction terminée en {elapsed:.1f}s")
        print(f"   Frames extraites: {len(frames)}")
        
        return {
            'video_info': video_info,
            'output_dir': str(frames_dir),
            'frame_count': len(frames),
            'frames': [str(f) for f in frames],
            'extraction_time': elapsed
        }


def extract_frames_from_video(video_path: str, 
                               output_dir: str,
                               fps: float = 2.0) -> Dict[str, Any]:
    """
    Fonction utilitaire pour extraction rapide.
    
    Args:
        video_path: Chemin vidéo source
        output_dir: Dossier de sortie
        fps: Frames par seconde
        
    Returns:
        Résultat de l'extraction
    """
    extractor = FrameExtractor(output_dir, fps=fps)
    return extractor.extract_frames(video_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_frames_from_video(
            sys.argv[1],
            "./test_extraction",
            fps=2.0
        )
        print(json.dumps(result, indent=2))
