#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate ALCHIMISTE - ESRGAN Upscaler
Upscale frames via Real-ESRGAN x4plus.

1080p → 4320p (puis crop/resize vers 4K si nécessaire).
Utilise realesrgan-ncnn-vulkan pour GPU Vulkan (compatible Colab).

Philosophie: L'alchimie des pixels - transformer le plomb en or.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

ESRGAN_BINARY = "realesrgan-ncnn-vulkan"
ESRGAN_MODEL = "realesrgan-x4plus"
ESRGAN_SCALE_FACTOR = 4

ESRGAN_MODELS = {
    "realesrgan-x4plus": {
        "description": "General purpose x4 upscaler (recommended)",
        "scale": 4
    },
    "realesrgan-x4plus-anime": {
        "description": "Anime/cartoon optimized x4 upscaler",
        "scale": 4
    },
    "realesr-animevideov3": {
        "description": "Anime video optimized (faster)",
        "scale": 4
    }
}


class ESRGANUpscaler:
    """
    Upscale frames via Real-ESRGAN x4plus.
    1080p → 4320p (puis crop/resize vers 4K si nécessaire).
    
    Utilise realesrgan-ncnn-vulkan pour GPU Vulkan (compatible Colab).
    
    Pipeline:
    1. Vérifie l'installation de realesrgan-ncnn-vulkan
    2. Traite les frames par batch (ou dossier complet)
    3. Applique Real-ESRGAN x4plus pour upscale 4x
    4. Retourne les chemins des frames upscalées
    
    Usage:
        upscaler = ESRGANUpscaler()
        if upscaler.check_installation():
            result = upscaler.upscale_frames(input_dir, output_dir)
    """
    
    def __init__(
        self, 
        model: str = ESRGAN_MODEL,
        scale_factor: int = ESRGAN_SCALE_FACTOR,
        verbose: bool = True
    ):
        """
        Args:
            model: Modèle ESRGAN à utiliser
            scale_factor: Facteur d'upscale (4 par défaut)
            verbose: Affiche les logs
        """
        self.model = model
        self.scale_factor = scale_factor
        self.verbose = verbose
        self.binary = ESRGAN_BINARY
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"🔮 [ESRGANUpscaler] {message}")
    
    def check_installation(self) -> bool:
        """
        Vérifie que realesrgan-ncnn-vulkan est installé et accessible.
        
        Returns:
            True si installé, False sinon
        """
        if shutil.which(self.binary):
            self._log(f"✓ {self.binary} trouvé dans PATH")
            return True
        
        try:
            result = subprocess.run(
                [self.binary, "-h"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                self._log(f"✓ {self.binary} accessible")
                return True
        except FileNotFoundError:
            self._log(f"⚠️ {self.binary} non trouvé")
        except subprocess.TimeoutExpired:
            self._log(f"⚠️ {self.binary} timeout")
        except Exception as e:
            self._log(f"⚠️ Erreur vérification: {e}")
        
        return False
    
    def get_version(self) -> Optional[str]:
        """
        Retourne la version de realesrgan-ncnn-vulkan.
        
        Returns:
            String de version ou None
        """
        try:
            result = subprocess.run(
                [self.binary, "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'version' in line.lower():
                    return line.strip()
            return "Unknown version"
        except Exception:
            return None
    
    def upscale_frames(
        self, 
        input_dir: str, 
        output_dir: str,
        model: Optional[str] = None,
        tile_size: int = 0,
        gpu_id: int = 0
    ) -> Dict[str, Any]:
        """
        Upscale tous les frames d'un dossier.
        
        Args:
            input_dir: Dossier des frames source
            output_dir: Dossier destination
            model: Modèle ESRGAN (défaut: realesrgan-x4plus)
            tile_size: Taille des tuiles (0 = auto)
            gpu_id: ID du GPU à utiliser
            
        Returns:
            Dict avec les résultats du traitement
        """
        model = model or self.model
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Dossier input non trouvé: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        input_frames = list(input_path.glob("*.png"))
        if not input_frames:
            input_frames = list(input_path.glob("*.jpg")) + list(input_path.glob("*.jpeg"))
        
        if not input_frames:
            raise ValueError(f"Aucune frame trouvée dans {input_dir}")
        
        self._log(f"ESRGAN: {input_dir} → {output_dir} (x{self.scale_factor})")
        self._log(f"  Model: {model}")
        self._log(f"  Frames à traiter: {len(input_frames)}")
        
        cmd = [
            self.binary,
            "-i", str(input_path),
            "-o", str(output_path),
            "-n", model,
            "-s", str(self.scale_factor),
            "-f", "png",
            "-g", str(gpu_id)
        ]
        
        if tile_size > 0:
            cmd.extend(["-t", str(tile_size)])
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            if result.stderr and self.verbose:
                self._log(f"  stderr: {result.stderr[:200]}")
                
        except subprocess.CalledProcessError as e:
            self._log(f"❌ ESRGAN failed: {e.stderr}")
            raise RuntimeError(f"ESRGAN failed: {e.stderr}")
        
        output_frames = list(output_path.glob("*.png"))
        
        self._log(f"✓ Upscale terminé: {len(output_frames)} frames")
        
        return {
            "status": "success",
            "input_dir": str(input_path),
            "output_dir": str(output_path),
            "scale_factor": self.scale_factor,
            "model": model,
            "frames_processed": len(output_frames),
            "input_frames": len(input_frames)
        }
    
    def upscale_single_frame(
        self, 
        input_path: str, 
        output_path: str,
        model: Optional[str] = None
    ) -> str:
        """
        Upscale une seule frame.
        
        Args:
            input_path: Chemin de la frame source
            output_path: Chemin de destination
            model: Modèle ESRGAN (optionnel)
            
        Returns:
            Chemin de la frame upscalée
        """
        model = model or self.model
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.binary,
            "-i", input_path,
            "-o", output_path,
            "-n", model,
            "-s", str(self.scale_factor)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self._log(f"✓ Upscale frame: {input_path} → {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ESRGAN frame failed: {e.stderr}")
    
    def upscale_frames_batch(
        self,
        frames: List[str],
        output_dir: str,
        model: Optional[str] = None
    ) -> List[str]:
        """
        Upscale une liste de frames spécifiques.
        
        Args:
            frames: Liste des chemins de frames
            output_dir: Dossier de destination
            model: Modèle ESRGAN (optionnel)
            
        Returns:
            Liste des chemins des frames upscalées
        """
        model = model or self.model
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        upscaled_frames = []
        
        for frame_path in frames:
            frame_name = Path(frame_path).name
            out_frame = str(output_path / frame_name)
            
            try:
                self.upscale_single_frame(frame_path, out_frame, model)
                upscaled_frames.append(out_frame)
            except RuntimeError as e:
                self._log(f"⚠️ Erreur frame {frame_name}: {e}")
        
        return upscaled_frames
    
    def estimate_vram_usage(self, resolution: tuple) -> float:
        """
        Estime l'utilisation VRAM pour une résolution donnée.
        
        Args:
            resolution: Tuple (width, height)
            
        Returns:
            VRAM estimée en GB
        """
        width, height = resolution
        pixels = width * height
        vram_per_pixel = 0.00000025
        base_vram = 1.5
        
        estimated_vram = base_vram + (pixels * vram_per_pixel * self.scale_factor)
        
        return round(estimated_vram, 2)
    
    def get_recommended_tile_size(self, resolution: tuple, vram_gb: float = 16.0) -> int:
        """
        Calcule la taille de tuile recommandée selon VRAM disponible.
        
        Args:
            resolution: Résolution d'entrée
            vram_gb: VRAM disponible en GB
            
        Returns:
            Taille de tuile recommandée (0 = pas de tiling)
        """
        estimated = self.estimate_vram_usage(resolution)
        
        if estimated < vram_gb * 0.8:
            return 0
        
        if vram_gb >= 16:
            return 512
        elif vram_gb >= 8:
            return 256
        elif vram_gb >= 4:
            return 128
        else:
            return 64


if __name__ == "__main__":
    print("=" * 60)
    print("🔮 ESRGAN UPSCALER - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   ESRGAN_BINARY: {ESRGAN_BINARY}")
    print(f"   ESRGAN_MODEL: {ESRGAN_MODEL}")
    print(f"   ESRGAN_SCALE_FACTOR: {ESRGAN_SCALE_FACTOR}")
    
    print(f"\n📋 Modèles disponibles:")
    for model, info in ESRGAN_MODELS.items():
        print(f"   {model}: {info['description']} (x{info['scale']})")
    
    upscaler = ESRGANUpscaler(verbose=True)
    
    print(f"\n🔧 Vérification installation:")
    installed = upscaler.check_installation()
    print(f"   Installé: {installed}")
    
    if installed:
        version = upscaler.get_version()
        print(f"   Version: {version}")
    
    print(f"\n📊 Estimation VRAM:")
    for res_name, res in [("1080p", (1920, 1080)), ("4K", (3840, 2160))]:
        vram = upscaler.estimate_vram_usage(res)
        tile = upscaler.get_recommended_tile_size(res, vram_gb=16)
        print(f"   {res_name}: ~{vram}GB VRAM, tile={tile}")
    
    print("\n✅ Module esrgan_upscaler.py fonctionnel")
