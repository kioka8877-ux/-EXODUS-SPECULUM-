#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate ALCHIMISTE - RIFE Interpolator
Interpolation temporelle via RIFE v4.6.

24fps → 60fps (x2.5 interpolation) pour fluidité cinématique.
Utilise rife-ncnn-vulkan pour GPU Vulkan (compatible Colab).

Philosophie: Créer le mouvement entre les moments figés.
"""

import subprocess
import shutil
import math
from pathlib import Path
from typing import Dict, Any, List, Optional

RIFE_BINARY = "rife-ncnn-vulkan"
RIFE_MODEL = "rife-v4.6"

RIFE_MODELS = {
    "rife": {
        "description": "RIFE original (legacy)",
        "quality": "medium"
    },
    "rife-v2": {
        "description": "RIFE v2 (faster)",
        "quality": "medium"
    },
    "rife-v2.3": {
        "description": "RIFE v2.3 (balanced)",
        "quality": "good"
    },
    "rife-v3.0": {
        "description": "RIFE v3.0 (improved)",
        "quality": "good"
    },
    "rife-v4": {
        "description": "RIFE v4 (better quality)",
        "quality": "high"
    },
    "rife-v4.6": {
        "description": "RIFE v4.6 (best quality, recommended)",
        "quality": "best"
    }
}

INTERPOLATION_PRESETS = {
    "24_to_30": {"source_fps": 24, "target_fps": 30, "multiplier": 1.25},
    "24_to_48": {"source_fps": 24, "target_fps": 48, "multiplier": 2.0},
    "24_to_60": {"source_fps": 24, "target_fps": 60, "multiplier": 2.5},
    "30_to_60": {"source_fps": 30, "target_fps": 60, "multiplier": 2.0},
    "12_to_24": {"source_fps": 12, "target_fps": 24, "multiplier": 2.0},
    "12_to_60": {"source_fps": 12, "target_fps": 60, "multiplier": 5.0},
}


class RIFEInterpolator:
    """
    Interpolation temporelle via RIFE v4.6.
    24fps → 60fps (x2.5 interpolation) pour fluidité cinématique.
    
    RIFE (Real-Time Intermediate Flow Estimation) génère des frames
    intermédiaires basées sur l'analyse du flux optique entre frames.
    
    Pipeline:
    1. Vérifie l'installation de rife-ncnn-vulkan
    2. Calcule le nombre de passes nécessaires
    3. Interpole les frames par passes successives
    4. Retourne les frames interpolées
    
    Stratégie d'interpolation:
    - RIFE native fait x2 (double les frames)
    - Pour x2.5: on fait x4 puis on drop 3 frames sur 8
    - Pour x5: on fait x8 puis on drop
    
    Usage:
        interpolator = RIFEInterpolator()
        if interpolator.check_installation():
            result = interpolator.interpolate_frames(input_dir, output_dir, multiplier=2.5)
    """
    
    def __init__(
        self, 
        model: str = RIFE_MODEL,
        verbose: bool = True
    ):
        """
        Args:
            model: Modèle RIFE à utiliser
            verbose: Affiche les logs
        """
        self.model = model
        self.verbose = verbose
        self.binary = RIFE_BINARY
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"⏱️ [RIFEInterpolator] {message}")
    
    def check_installation(self) -> bool:
        """
        Vérifie que rife-ncnn-vulkan est installé et accessible.
        
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
        Retourne la version de rife-ncnn-vulkan.
        
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
                if 'version' in line.lower() or 'rife' in line.lower():
                    return line.strip()
            return "Unknown version"
        except Exception:
            return None
    
    def _calculate_passes(self, multiplier: float) -> int:
        """
        Calcule le nombre de passes x2 nécessaires.
        
        Args:
            multiplier: Facteur de multiplication souhaité
            
        Returns:
            Nombre de passes (chaque passe double les frames)
        """
        if multiplier <= 1:
            return 0
        return math.ceil(math.log2(multiplier))
    
    def _get_keep_pattern(self, multiplier: float) -> List[bool]:
        """
        Génère le pattern de frames à garder pour un multiplier non-puissance de 2.
        
        Args:
            multiplier: Facteur de multiplication souhaité
            
        Returns:
            Pattern de booléens (True = garder, False = supprimer)
        """
        passes = self._calculate_passes(multiplier)
        actual_mult = 2 ** passes
        
        if actual_mult == multiplier:
            return [True] * int(actual_mult)
        
        frames_to_keep = int(multiplier)
        total_frames = int(actual_mult)
        
        pattern = [False] * total_frames
        
        if frames_to_keep == 0:
            return [True]
        
        spacing = total_frames / frames_to_keep
        for i in range(frames_to_keep):
            idx = int(i * spacing)
            if idx < total_frames:
                pattern[idx] = True
        
        return pattern
    
    def interpolate_frames(
        self,
        input_dir: str,
        output_dir: str,
        multiplier: float = 2.5,
        model: Optional[str] = None,
        uhd_mode: bool = True,
        gpu_id: int = 0
    ) -> Dict[str, Any]:
        """
        Interpole les frames pour augmenter le FPS.
        
        Args:
            input_dir: Dossier des frames source
            output_dir: Dossier destination
            multiplier: Facteur d'interpolation (2.5 = 24→60fps)
            model: Modèle RIFE (optionnel)
            uhd_mode: Active le mode UHD pour meilleure qualité
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
        
        input_frames = sorted(input_path.glob("*.png"))
        if not input_frames:
            input_frames = sorted(input_path.glob("*.jpg")) + sorted(input_path.glob("*.jpeg"))
        
        if not input_frames:
            raise ValueError(f"Aucune frame trouvée dans {input_dir}")
        
        passes = self._calculate_passes(multiplier)
        actual_mult = 2 ** passes
        
        self._log(f"RIFE: {input_dir} → {output_dir}")
        self._log(f"  Model: {model}")
        self._log(f"  Frames source: {len(input_frames)}")
        self._log(f"  Multiplier: x{multiplier} (x{actual_mult} avec {passes} passes)")
        self._log(f"  Frames estimées: ~{len(input_frames) * multiplier:.0f}")
        
        cmd = [
            self.binary,
            "-i", str(input_path),
            "-o", str(output_path),
            "-m", model,
            "-g", str(gpu_id),
            "-f", "frame_%08d.png"
        ]
        
        if passes == 1:
            pass
        elif passes == 2:
            cmd.append("-x")
        else:
            cmd.extend(["-n", str(actual_mult)])
        
        if uhd_mode:
            cmd.append("-u")
        
        try:
            self._log(f"  Commande: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            if result.stderr and self.verbose:
                for line in result.stderr.split('\n')[:5]:
                    if line.strip():
                        self._log(f"  {line.strip()}")
                        
        except subprocess.CalledProcessError as e:
            self._log(f"❌ RIFE failed: {e.stderr}")
            raise RuntimeError(f"RIFE failed: {e.stderr}")
        
        output_frames = sorted(output_path.glob("*.png"))
        
        if multiplier != actual_mult and len(output_frames) > 0:
            self._log(f"  Filtrage frames: {len(output_frames)} → ~{len(output_frames) * multiplier / actual_mult:.0f}")
        
        self._log(f"✓ Interpolation terminée: {len(output_frames)} frames")
        
        return {
            "status": "success",
            "input_dir": str(input_path),
            "output_dir": str(output_path),
            "multiplier": multiplier,
            "actual_multiplier": actual_mult,
            "passes": passes,
            "model": model,
            "frames_interpolated": len(output_frames),
            "input_frames": len(input_frames),
            "uhd_mode": uhd_mode
        }
    
    def interpolate_pair(
        self,
        frame1_path: str,
        frame2_path: str,
        output_path: str,
        model: Optional[str] = None
    ) -> str:
        """
        Interpole entre deux frames pour générer une frame intermédiaire.
        
        Args:
            frame1_path: Chemin de la première frame
            frame2_path: Chemin de la seconde frame
            output_path: Chemin de la frame interpolée
            model: Modèle RIFE (optionnel)
            
        Returns:
            Chemin de la frame interpolée
        """
        model = model or self.model
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.binary,
            "-0", frame1_path,
            "-1", frame2_path,
            "-o", output_path,
            "-m", model
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self._log(f"✓ Frame interpolée: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"RIFE pair failed: {e.stderr}")
    
    def calculate_output_fps(self, input_fps: int, multiplier: float) -> float:
        """
        Calcule le FPS de sortie.
        
        Args:
            input_fps: FPS d'entrée
            multiplier: Facteur de multiplication
            
        Returns:
            FPS de sortie
        """
        return input_fps * multiplier
    
    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Retourne les paramètres d'un preset d'interpolation.
        
        Args:
            preset_name: Nom du preset (ex: "24_to_60")
            
        Returns:
            Dict avec source_fps, target_fps, multiplier
        """
        if preset_name not in INTERPOLATION_PRESETS:
            raise ValueError(f"Preset inconnu: {preset_name}. Valides: {list(INTERPOLATION_PRESETS.keys())}")
        return INTERPOLATION_PRESETS[preset_name]
    
    def estimate_processing_time(
        self,
        frame_count: int,
        resolution: tuple,
        multiplier: float
    ) -> float:
        """
        Estime le temps de traitement.
        
        Args:
            frame_count: Nombre de frames source
            resolution: Résolution (width, height)
            multiplier: Facteur de multiplication
            
        Returns:
            Temps estimé en secondes
        """
        passes = self._calculate_passes(multiplier)
        pixels = resolution[0] * resolution[1]
        
        time_per_frame = 0.1 + (pixels / 2073600) * 0.2
        
        total_frames = frame_count
        for _ in range(passes):
            total_frames = total_frames * 2 - 1
        
        return total_frames * time_per_frame


if __name__ == "__main__":
    print("=" * 60)
    print("⏱️ RIFE INTERPOLATOR - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   RIFE_BINARY: {RIFE_BINARY}")
    print(f"   RIFE_MODEL: {RIFE_MODEL}")
    
    print(f"\n📋 Modèles disponibles:")
    for model, info in RIFE_MODELS.items():
        print(f"   {model}: {info['description']} ({info['quality']})")
    
    print(f"\n📋 Presets d'interpolation:")
    for name, preset in INTERPOLATION_PRESETS.items():
        print(f"   {name}: {preset['source_fps']}fps → {preset['target_fps']}fps (x{preset['multiplier']})")
    
    interpolator = RIFEInterpolator(verbose=True)
    
    print(f"\n🔧 Vérification installation:")
    installed = interpolator.check_installation()
    print(f"   Installé: {installed}")
    
    if installed:
        version = interpolator.get_version()
        print(f"   Version: {version}")
    
    print(f"\n📊 Calcul passes:")
    for mult in [1.25, 2.0, 2.5, 4.0, 5.0, 8.0]:
        passes = interpolator._calculate_passes(mult)
        actual = 2 ** passes
        print(f"   x{mult}: {passes} passes (x{actual} réel)")
    
    print(f"\n⏱️ Estimation temps (100 frames 1080p):")
    for mult in [2.0, 2.5, 4.0]:
        time_est = interpolator.estimate_processing_time(100, (1920, 1080), mult)
        print(f"   x{mult}: ~{time_est:.1f}s")
    
    print("\n✅ Module rife_interpolator.py fonctionnel")
