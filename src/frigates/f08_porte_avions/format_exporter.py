#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS - Format Exporter
Export multi-plateformes avec conversion de format intelligente.

Ce module exporte la vidéo master vers les différents formats plateformes:
- YouTube 4K (3840x2160 @ 60fps, H.265)
- YouTube 1080p (1920x1080 @ 60fps, H.264)
- TikTok (1080x1920 vertical @ 60fps, max 3min)
- Instagram Reels (1080x1920 vertical @ 30fps, max 90s)
- Instagram Feed (1080x1080 square @ 30fps, max 60s)

Features:
- Smart crop pour conversion horizontal → vertical
- Point of Interest (POI) pour centrer le crop
- Respect des limites de durée par plateforme

Usage:
    exporter = FormatExporter()
    
    output = exporter.export_for_platform(
        master_video="/path/to/master_4k.mp4",
        platform="tiktok",
        output_dir="/path/to/exports"
    )
    
    results = exporter.export_all_platforms(
        master_video="/path/to/master_4k.mp4",
        output_dir="/path/to/exports",
        platforms=["youtube_4k", "tiktok", "instagram_reels"]
    )
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PLATFORM_SPECS = {
    "youtube_4k": {
        "name": "YouTube 4K",
        "resolution": (3840, 2160),
        "fps": 60,
        "bitrate": "45M",
        "codec": "libx265",
        "audio_bitrate": "320k",
        "max_duration": None,
        "orientation": "horizontal"
    },
    "youtube_1080": {
        "name": "YouTube 1080p",
        "resolution": (1920, 1080),
        "fps": 60,
        "bitrate": "12M",
        "codec": "libx264",
        "audio_bitrate": "256k",
        "max_duration": None,
        "orientation": "horizontal"
    },
    "youtube_shorts": {
        "name": "YouTube Shorts",
        "resolution": (1080, 1920),
        "fps": 60,
        "bitrate": "10M",
        "codec": "libx264",
        "audio_bitrate": "192k",
        "max_duration": 60,
        "orientation": "vertical"
    },
    "tiktok": {
        "name": "TikTok",
        "resolution": (1080, 1920),
        "fps": 60,
        "bitrate": "10M",
        "codec": "libx264",
        "audio_bitrate": "192k",
        "max_duration": 180,
        "orientation": "vertical"
    },
    "instagram_reels": {
        "name": "Instagram Reels",
        "resolution": (1080, 1920),
        "fps": 30,
        "bitrate": "8M",
        "codec": "libx264",
        "audio_bitrate": "128k",
        "max_duration": 90,
        "orientation": "vertical"
    },
    "instagram_feed": {
        "name": "Instagram Feed",
        "resolution": (1080, 1080),
        "fps": 30,
        "bitrate": "6M",
        "codec": "libx264",
        "audio_bitrate": "128k",
        "max_duration": 60,
        "orientation": "square"
    },
    "twitter": {
        "name": "Twitter/X",
        "resolution": (1920, 1080),
        "fps": 60,
        "bitrate": "10M",
        "codec": "libx264",
        "audio_bitrate": "256k",
        "max_duration": 140,
        "orientation": "horizontal"
    },
    "linkedin": {
        "name": "LinkedIn",
        "resolution": (1920, 1080),
        "fps": 30,
        "bitrate": "8M",
        "codec": "libx264",
        "audio_bitrate": "192k",
        "max_duration": 600,
        "orientation": "horizontal"
    }
}


class FormatExporter:
    """
    Exporte la vidéo master vers les différents formats plateformes.
    
    Features:
    - Conversion de résolution avec smart crop
    - Adaptation du framerate
    - Respect des limites de durée
    - Point of Interest (POI) pour centrer le crop vertical
    
    Usage:
        exporter = FormatExporter()
        
        output = exporter.export_for_platform(
            master_video="master_4k.mp4",
            platform="tiktok",
            output_dir="exports/"
        )
    """
    
    PLATFORM_SPECS = PLATFORM_SPECS
    
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
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Récupère les informations d'une vidéo via ffprobe.
        
        Args:
            video_path: Chemin de la vidéo
            
        Returns:
            Dict avec durée, fps, résolution
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
            return {"error": result.stderr, "width": 3840, "height": 2160, "duration_sec": 30}
        
        import json
        try:
            info = json.loads(result.stdout)
            
            video_stream = None
            for stream in info.get("streams", []):
                if stream["codec_type"] == "video":
                    video_stream = stream
                    break
            
            duration = float(info.get("format", {}).get("duration", 30))
            
            return {
                "duration_sec": duration,
                "width": int(video_stream.get("width", 3840)) if video_stream else 3840,
                "height": int(video_stream.get("height", 2160)) if video_stream else 2160
            }
        except (json.JSONDecodeError, KeyError):
            return {"width": 3840, "height": 2160, "duration_sec": 30}
    
    def export_for_platform(
        self,
        master_video: str,
        platform: str,
        output_dir: str,
        smart_crop_poi: Optional[Tuple[float, float]] = None,
        custom_duration: Optional[float] = None
    ) -> str:
        """
        Exporte pour une plateforme spécifique avec conversion de format.
        
        Args:
            master_video: Vidéo master (typiquement 4K horizontal)
            platform: Nom de la plateforme (youtube_4k, tiktok, etc.)
            output_dir: Dossier de sortie
            smart_crop_poi: Point of Interest (x, y) en ratio [0-1] pour centrer le crop
            custom_duration: Durée personnalisée (override max_duration)
            
        Returns:
            Chemin de la vidéo exportée
        """
        if platform not in self.PLATFORM_SPECS:
            raise ValueError(f"Plateforme inconnue: {platform}. Valides: {list(self.PLATFORM_SPECS.keys())}")
        
        spec = self.PLATFORM_SPECS[platform]
        self._log(f"   📤 Export {spec['name']}")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{output_dir}/{platform}_export.mp4"
        
        video_info = self.get_video_info(master_video)
        src_width = video_info.get("width", 3840)
        src_height = video_info.get("height", 2160)
        src_duration = video_info.get("duration_sec", 30)
        
        target_width, target_height = spec["resolution"]
        
        filters = []
        
        src_ratio = src_width / src_height
        target_ratio = target_width / target_height
        
        if spec["orientation"] == "vertical" and src_ratio > 1:
            crop_width = int(src_height * target_ratio)
            
            if smart_crop_poi:
                x_offset = int((src_width - crop_width) * smart_crop_poi[0])
            else:
                x_offset = (src_width - crop_width) // 2
            
            x_offset = max(0, min(x_offset, src_width - crop_width))
            filters.append(f"crop={crop_width}:{src_height}:{x_offset}:0")
            self._log(f"      Smart crop: {crop_width}x{src_height} @ x={x_offset}")
        
        elif spec["orientation"] == "square" and src_ratio > 1:
            crop_size = min(src_width, src_height)
            
            if smart_crop_poi:
                x_offset = int((src_width - crop_size) * smart_crop_poi[0])
            else:
                x_offset = (src_width - crop_size) // 2
            
            filters.append(f"crop={crop_size}:{crop_size}:{x_offset}:0")
            self._log(f"      Square crop: {crop_size}x{crop_size}")
        
        filters.append(f"scale={target_width}:{target_height}")
        
        duration = custom_duration or src_duration
        if spec["max_duration"] and duration > spec["max_duration"]:
            duration = spec["max_duration"]
            self._log(f"      Durée limitée à {duration}s")
        
        filter_str = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-y",
            "-i", master_video
        ]
        
        if duration < src_duration:
            cmd.extend(["-t", str(duration)])
        
        cmd.extend([
            "-vf", filter_str,
            "-c:v", spec["codec"],
            "-b:v", spec["bitrate"],
            "-r", str(spec["fps"]),
            "-c:a", "aac",
            "-b:a", spec["audio_bitrate"],
            "-ar", "48000",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self._log(f"   ❌ Erreur: {result.stderr}")
            raise RuntimeError(f"FFmpeg export failed: {result.stderr}")
        
        self._log(f"      ✓ {target_width}x{target_height} @ {spec['fps']}fps")
        
        return output_path
    
    def export_all_platforms(
        self,
        master_video: str,
        output_dir: str,
        platforms: Optional[List[str]] = None,
        smart_crop_poi: Optional[Tuple[float, float]] = None
    ) -> Dict[str, str]:
        """
        Exporte vers toutes les plateformes demandées.
        
        Args:
            master_video: Vidéo master
            output_dir: Dossier de sortie
            platforms: Liste des plateformes (défaut: toutes)
            smart_crop_poi: POI pour le crop
            
        Returns:
            Dict {platform: output_path ou error}
        """
        if platforms is None:
            platforms = list(self.PLATFORM_SPECS.keys())
        
        self._log(f"\n📤 Export multi-plateformes: {len(platforms)} cibles")
        
        results = {}
        for platform in platforms:
            try:
                output = self.export_for_platform(
                    master_video,
                    platform,
                    output_dir,
                    smart_crop_poi
                )
                results[platform] = output
            except Exception as e:
                results[platform] = f"ERROR: {e}"
                self._log(f"   ❌ {platform}: {e}")
        
        success_count = sum(1 for v in results.values() if not v.startswith("ERROR"))
        self._log(f"\n   ✓ {success_count}/{len(platforms)} exports réussis")
        
        return results
    
    def get_platform_info(self, platform: str) -> Dict[str, Any]:
        """
        Retourne les spécifications d'une plateforme.
        
        Args:
            platform: Nom de la plateforme
            
        Returns:
            Dict avec les specs
        """
        if platform not in self.PLATFORM_SPECS:
            return {"error": f"Unknown platform: {platform}"}
        
        spec = self.PLATFORM_SPECS[platform].copy()
        spec["platform_id"] = platform
        return spec
    
    def list_platforms(self) -> List[Dict[str, Any]]:
        """Liste toutes les plateformes disponibles avec leurs specs."""
        return [
            {"id": k, **v}
            for k, v in self.PLATFORM_SPECS.items()
        ]


if __name__ == "__main__":
    print("=" * 60)
    print("📤 FORMAT EXPORTER - Test Mode")
    print("=" * 60)
    
    exporter = FormatExporter(verbose=True)
    
    print(f"\n🔧 FFmpeg disponible: {exporter.check_ffmpeg()}")
    
    print(f"\n📋 Plateformes disponibles:")
    for platform_id, spec in PLATFORM_SPECS.items():
        res = f"{spec['resolution'][0]}x{spec['resolution'][1]}"
        max_dur = f"{spec['max_duration']}s" if spec['max_duration'] else "∞"
        print(f"   {platform_id}:")
        print(f"      {spec['name']}: {res} @ {spec['fps']}fps, max {max_dur}")
        print(f"      Codec: {spec['codec']}, Bitrate: {spec['bitrate']}")
    
    print(f"\n📊 Groupes par orientation:")
    orientations = {}
    for pid, spec in PLATFORM_SPECS.items():
        orient = spec['orientation']
        if orient not in orientations:
            orientations[orient] = []
        orientations[orient].append(pid)
    
    for orient, platforms in orientations.items():
        print(f"   {orient}: {', '.join(platforms)}")
    
    print("\n✅ Module format_exporter.py fonctionnel")
