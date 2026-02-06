#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS - FFmpeg Encoder
Encodage vidéo finale H.265/H.264 haute qualité.

Ce module assemble les frames rendues en vidéo finale via FFmpeg.
Supporte H.264 (compatibilité maximale) et H.265/HEVC (qualité optimale).

Profils:
- compatibility: H.264, CRF 18, preset slow - Pour tous les appareils
- quality: H.265/HEVC, CRF 20, main10 - Qualité maximale, taille réduite

Usage:
    encoder = FFmpegEncoder()
    result = encoder.encode_from_frames(
        frames_dir="/path/to/frames",
        output_path="/path/to/output.mp4",
        fps=60,
        codec_profile="quality"
    )
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

CODEC_PROFILES = {
    "compatibility": {
        "codec": "libx264",
        "preset": "slow",
        "crf": 18,
        "profile": "high",
        "level": "4.1",
        "pix_fmt": "yuv420p"
    },
    "quality": {
        "codec": "libx265",
        "preset": "slow",
        "crf": 20,
        "profile": "main10",
        "pix_fmt": "yuv420p10le"
    },
    "fast": {
        "codec": "libx264",
        "preset": "fast",
        "crf": 23,
        "profile": "high",
        "level": "4.1",
        "pix_fmt": "yuv420p"
    }
}


class FFmpegEncoder:
    """
    Encode les frames en vidéo finale via FFmpeg.
    Supporte H.264 (compatibilité) et H.265/HEVC (qualité).
    
    Usage:
        encoder = FFmpegEncoder()
        
        result = encoder.encode_from_frames(
            frames_dir="/path/to/frames",
            output_path="output.mp4",
            fps=60,
            codec_profile="quality",
            audio_path="/path/to/audio.wav"
        )
    """
    
    CODEC_PROFILES = CODEC_PROFILES
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs détaillés
        """
        self.verbose = verbose
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(message)
    
    def check_ffmpeg(self) -> bool:
        """Vérifie que FFmpeg est installé."""
        return shutil.which("ffmpeg") is not None
    
    def encode_from_frames(
        self,
        frames_dir: str,
        output_path: str,
        fps: int = 60,
        codec_profile: str = "quality",
        audio_path: Optional[str] = None,
        frame_pattern: str = "frame_%04d.png"
    ) -> Dict[str, Any]:
        """
        Encode une séquence de frames en vidéo.
        
        Args:
            frames_dir: Dossier contenant frame_0001.png, frame_0002.png, etc.
            output_path: Chemin de sortie .mp4
            fps: Framerate (60 pour mode conquérant)
            codec_profile: "compatibility" (H.264), "quality" (H.265), ou "fast"
            audio_path: Optionnel - piste audio à mixer
            frame_pattern: Pattern des noms de frames
            
        Returns:
            Dict avec les infos d'encodage
        """
        self._log(f"   🎬 Encodage depuis frames: {frames_dir}")
        
        if codec_profile not in self.CODEC_PROFILES:
            raise ValueError(f"Profil inconnu: {codec_profile}. Valides: {list(self.CODEC_PROFILES.keys())}")
        
        profile = self.CODEC_PROFILES[codec_profile]
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", f"{frames_dir}/{frame_pattern}",
        ]
        
        if audio_path:
            cmd.extend(["-i", audio_path])
            
        cmd.extend([
            "-c:v", profile["codec"],
            "-preset", profile["preset"],
            "-crf", str(profile["crf"]),
            "-pix_fmt", profile.get("pix_fmt", "yuv420p"),
        ])
        
        if profile.get("profile"):
            if profile["codec"] == "libx264":
                cmd.extend(["-profile:v", profile["profile"]])
            elif profile["codec"] == "libx265":
                cmd.extend(["-x265-params", f"profile={profile['profile']}"])
        
        if profile.get("level") and profile["codec"] == "libx264":
            cmd.extend(["-level:v", profile["level"]])
        
        if audio_path:
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "320k",
                "-ar", "48000"
            ])
        
        cmd.extend(["-movflags", "+faststart"])
        cmd.append(output_path)
        
        self._log(f"   📼 Codec: {profile['codec']} (CRF {profile['crf']})")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self._log(f"   ❌ Erreur FFmpeg: {result.stderr}")
            raise RuntimeError(f"FFmpeg encode failed: {result.stderr}")
        
        self._log(f"   ✓ Encodé: {output_path}")
        
        return {
            "output": output_path,
            "codec": profile["codec"],
            "fps": fps,
            "profile": codec_profile,
            "has_audio": audio_path is not None
        }
        
    def encode_from_video(
        self,
        input_video: str,
        output_path: str,
        audio_path: Optional[str] = None,
        codec_profile: str = "quality"
    ) -> Dict[str, Any]:
        """
        Ré-encode une vidéo existante avec optionnellement une nouvelle piste audio.
        
        Args:
            input_video: Vidéo source
            output_path: Chemin de sortie
            audio_path: Optionnel - nouvelle piste audio
            codec_profile: Profil d'encodage
            
        Returns:
            Dict avec les infos d'encodage
        """
        self._log(f"   🎬 Ré-encodage: {input_video}")
        
        profile = self.CODEC_PROFILES.get(codec_profile, self.CODEC_PROFILES["quality"])
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["ffmpeg", "-y", "-i", input_video]
        
        if audio_path:
            cmd.extend(["-i", audio_path, "-map", "0:v", "-map", "1:a"])
            cmd.extend([
                "-c:v", profile["codec"],
                "-preset", profile["preset"],
                "-crf", str(profile["crf"]),
                "-pix_fmt", profile.get("pix_fmt", "yuv420p"),
                "-c:a", "aac",
                "-b:a", "320k",
                "-ar", "48000"
            ])
        else:
            cmd.extend(["-c:v", "copy"])
            cmd.extend(["-c:a", "copy"])
        
        cmd.extend(["-movflags", "+faststart"])
        cmd.append(output_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self._log(f"   ❌ Erreur FFmpeg: {result.stderr}")
            raise RuntimeError(f"FFmpeg encode failed: {result.stderr}")
        
        self._log(f"   ✓ Ré-encodé: {output_path}")
        
        return {
            "output": output_path,
            "has_audio": audio_path is not None,
            "codec": profile["codec"] if audio_path else "copy"
        }
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Récupère les informations d'une vidéo via ffprobe.
        
        Args:
            video_path: Chemin de la vidéo
            
        Returns:
            Dict avec durée, fps, résolution, etc.
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        import json
        try:
            info = json.loads(result.stdout)
            
            video_stream = None
            audio_stream = None
            for stream in info.get("streams", []):
                if stream["codec_type"] == "video" and not video_stream:
                    video_stream = stream
                elif stream["codec_type"] == "audio" and not audio_stream:
                    audio_stream = stream
            
            duration = float(info.get("format", {}).get("duration", 0))
            
            fps = 0
            if video_stream and "r_frame_rate" in video_stream:
                fps_parts = video_stream["r_frame_rate"].split("/")
                if len(fps_parts) == 2 and int(fps_parts[1]) != 0:
                    fps = int(fps_parts[0]) / int(fps_parts[1])
            
            return {
                "duration_sec": duration,
                "fps": fps,
                "width": int(video_stream.get("width", 0)) if video_stream else 0,
                "height": int(video_stream.get("height", 0)) if video_stream else 0,
                "video_codec": video_stream.get("codec_name") if video_stream else None,
                "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
                "has_audio": audio_stream is not None
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse ffprobe output"}


if __name__ == "__main__":
    print("=" * 60)
    print("🎬 FFMPEG ENCODER - Test Mode")
    print("=" * 60)
    
    encoder = FFmpegEncoder()
    
    print(f"\n🔧 FFmpeg disponible: {encoder.check_ffmpeg()}")
    
    print(f"\n📋 Profils disponibles:")
    for name, profile in CODEC_PROFILES.items():
        print(f"   {name}: {profile['codec']} CRF {profile['crf']}")
    
    print("\n✅ Module ffmpeg_encoder.py fonctionnel")
