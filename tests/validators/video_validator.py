"""
EXODUS-SPECULUM - Video Validator
Validator pour fichiers vidéo (F07 PORTE-AVIONS output).
"""
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from .base_validator import BaseValidator, ValidationResult


class VideoValidator(BaseValidator):
    """
    Validator pour fichiers vidéo MP4/MOV.
    
    Utilise ffprobe pour extraire les métadonnées et valider
    contre le contrat video_contract.json.
    
    Usage:
        validator = VideoValidator("contracts/video_contract.json")
        result = validator.validate("output/final_video.mp4")
    """
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        Valide un fichier vidéo.
        
        Args:
            file_path: Chemin vers le fichier vidéo
            
        Returns:
            ValidationResult avec métriques vidéo
        """
        errors: List[str] = []
        warnings: List[str] = []
        metrics: Dict[str, Any] = {}
        
        if err := self._check_file_exists(file_path):
            return ValidationResult(valid=False, errors=[err])
        
        if err := self._check_extension(file_path, [".mp4", ".mov", ".mkv"]):
            errors.append(err)
        
        metrics["size_mb"] = Path(file_path).stat().st_size / (1024 * 1024)
        
        probe_result = self._ffprobe(file_path)
        if probe_result is None:
            warnings.append("ffprobe not available, limited validation")
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metrics=metrics
            )
        
        video_stream = None
        audio_stream = None
        for stream in probe_result.get("streams", []):
            if stream.get("codec_type") == "video" and video_stream is None:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and audio_stream is None:
                audio_stream = stream
        
        if video_stream:
            metrics["width"] = video_stream.get("width", 0)
            metrics["height"] = video_stream.get("height", 0)
            metrics["codec"] = video_stream.get("codec_name", "unknown")
            
            fps_str = video_stream.get("r_frame_rate", "0/1")
            try:
                num, den = fps_str.split("/")
                metrics["fps"] = round(int(num) / int(den), 2)
            except:
                metrics["fps"] = 0
            
            metrics["duration_sec"] = float(video_stream.get("duration", 0))
            metrics["frame_count"] = int(video_stream.get("nb_frames", 0))
            
            bit_rate = video_stream.get("bit_rate")
            if bit_rate:
                metrics["bitrate_mbps"] = int(bit_rate) / 1_000_000
        else:
            errors.append("No video stream found")
        
        if audio_stream:
            metrics["audio_codec"] = audio_stream.get("codec_name", "unknown")
            metrics["audio_sample_rate"] = int(audio_stream.get("sample_rate", 0))
            metrics["audio_channels"] = audio_stream.get("channels", 0)
            metrics["has_audio"] = True
        else:
            metrics["has_audio"] = False
        
        if self.contract:
            errors.extend(self._validate_against_contract(metrics))
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _ffprobe(self, file_path: str) -> Optional[Dict]:
        """Exécute ffprobe et retourne les métadonnées JSON."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        return None
    
    def _validate_against_contract(self, metrics: Dict[str, Any]) -> List[str]:
        """Valide les métriques contre le contrat."""
        errors = []
        
        codec_list = self.contract.get("codec", {}).get("video", [])
        if codec_list and metrics.get("codec") not in codec_list:
            errors.append(f"Invalid codec: {metrics.get('codec')}, expected: {codec_list}")
        
        res_limits = self.contract.get("resolution", {})
        width = metrics.get("width", 0)
        height = metrics.get("height", 0)
        if "min" in res_limits:
            min_w, min_h = res_limits["min"]
            if width < min_w or height < min_h:
                errors.append(f"Resolution too low: {width}x{height}, min: {min_w}x{min_h}")
        if "max" in res_limits:
            max_w, max_h = res_limits["max"]
            if width > max_w or height > max_h:
                errors.append(f"Resolution too high: {width}x{height}, max: {max_w}x{max_h}")
        
        fps_limits = self.contract.get("fps", {})
        fps = metrics.get("fps", 0)
        if fps < fps_limits.get("min", 0):
            errors.append(f"FPS too low: {fps}, min: {fps_limits['min']}")
        if fps > fps_limits.get("max", float('inf')):
            errors.append(f"FPS too high: {fps}, max: {fps_limits['max']}")
        
        audio_contract = self.contract.get("audio", {})
        if audio_contract.get("required", False) and not metrics.get("has_audio"):
            errors.append("Audio track required but not found")
        
        return errors
