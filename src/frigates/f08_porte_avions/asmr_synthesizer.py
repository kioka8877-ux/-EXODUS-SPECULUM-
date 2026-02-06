#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS - ASMR Synthesizer
Sound Design immersif pour simuler une vraie visite iPhone.

Génère les couches audio ASMR:
- Pas sur carrelage synchronisés avec le walking bounce (1.8 Hz)
- Room tone de villa luxueuse
- Froissements de vêtements POV
- Respiration subtile synchronisée avec le breathing zoom (4s cycle)

Philosophie: L'Illusion de Présence
Transformer une vidéo 3D en "vraie visite filmée à l'iPhone" via un sound design
qui renforce l'illusion qu'une personne réelle filme en marchant.

Usage:
    synth = ASMRSynthesizer(assetshub_path="/path/to/assetshub")
    
    footsteps = synth.generate_footsteps_track(duration_sec=30.0)
    room_tone = synth.generate_room_tone(duration_sec=30.0)
    cloth = synth.generate_cloth_rustle(duration_sec=30.0)
    breathing = synth.generate_breathing(duration_sec=30.0)
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple

try:
    from scipy.io import wavfile
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    wavfile = None
    signal = None

SAMPLE_RATE = 48000

HANDHELD_Z_FREQ = 1.8
HANDHELD_BREATHING_CYCLE = 4.0

SAMPLE_PATHS = {
    "footsteps_tile": "audio/footsteps_tile_loop.wav",
    "footsteps_wood": "audio/footsteps_wood_loop.wav",
    "footsteps_carpet": "audio/footsteps_carpet_loop.wav",
    "room_tone_villa": "audio/room_tone_luxury.wav",
    "room_tone_modern": "audio/room_tone_modern.wav",
    "cloth_rustle": "audio/cloth_movement.wav",
    "breathing_subtle": "audio/breathing_female_subtle.wav",
    "wind_light": "audio/wind_through_window.wav",
    "ac_hum": "audio/ac_hum_subtle.wav"
}


class ASMRSynthesizer:
    """
    Génère les couches audio ASMR pour simuler une vraie visite iPhone.
    
    Couches:
    - Pas sur carrelage synchronisés avec le walking bounce
    - Room tone de villa luxueuse
    - Froissements de vêtements POV
    - Respiration subtile
    
    Usage:
        synth = ASMRSynthesizer(assetshub_path="/path/to/assetshub")
        footsteps = synth.generate_footsteps_track(duration_sec=30.0, walking_freq_hz=1.8)
    """
    
    SAMPLE_RATE = SAMPLE_RATE
    
    def __init__(self, assetshub_path: str, verbose: bool = True):
        """
        Args:
            assetshub_path: Chemin vers ASSETSHUB contenant les samples audio
            verbose: Affiche les logs détaillés
        """
        self.assetshub_path = assetshub_path
        self.verbose = verbose
        self._sample_cache: Dict[str, np.ndarray] = {}
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(message)
    
    def _load_sample(self, sample_key: str) -> Optional[np.ndarray]:
        """
        Charge un sample audio depuis ASSETSHUB.
        
        Args:
            sample_key: Clé du sample (footsteps_tile, room_tone_villa, etc.)
            
        Returns:
            Array numpy float32 normalisé [-1, 1] ou None si non disponible
        """
        if sample_key in self._sample_cache:
            return self._sample_cache[sample_key]
        
        if sample_key not in SAMPLE_PATHS:
            return None
        
        if not SCIPY_AVAILABLE:
            return None
        
        sample_path = f"{self.assetshub_path}/{SAMPLE_PATHS[sample_key]}"
        
        try:
            sr, data = wavfile.read(sample_path)
            
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0
            elif data.dtype == np.int32:
                data = data.astype(np.float32) / 2147483648.0
            elif data.dtype == np.float64:
                data = data.astype(np.float32)
            
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            if sr != self.SAMPLE_RATE:
                ratio = self.SAMPLE_RATE / sr
                new_length = int(len(data) * ratio)
                data = np.interp(
                    np.linspace(0, len(data) - 1, new_length),
                    np.arange(len(data)),
                    data
                ).astype(np.float32)
            
            self._sample_cache[sample_key] = data
            return data
            
        except (FileNotFoundError, IOError):
            return None
    
    def generate_footsteps_track(
        self,
        duration_sec: float,
        walking_freq_hz: float = HANDHELD_Z_FREQ,
        surface: str = "tile",
        volume: float = 0.5,
        stereo_width: float = 0.3
    ) -> np.ndarray:
        """
        Génère une piste de pas synchronisée avec le walking bounce.
        
        La fréquence des pas = HANDHELD_Z_FREQ (1.8 Hz = ~108 pas/minute)
        Chaque pic sinusoïdal du bounce = un pas.
        
        Args:
            duration_sec: Durée en secondes
            walking_freq_hz: Fréquence des pas (synced avec camera bounce)
            surface: Type de surface (tile, wood, carpet)
            volume: Volume relatif [0, 1]
            stereo_width: Largeur stéréo pour alternance L/R
            
        Returns:
            Array numpy float32 mono ou stéréo
        """
        num_samples = int(duration_sec * self.SAMPLE_RATE)
        output = np.zeros(num_samples, dtype=np.float32)
        
        sample_key = f"footsteps_{surface}"
        footstep_sample = self._load_sample(sample_key)
        
        if footstep_sample is None:
            self._log(f"   ⚠️ Sample {sample_key} non trouvé, fallback synthétique")
            footstep_sample = self._generate_synthetic_footstep()
        
        step_interval = 1.0 / walking_freq_hz
        num_steps = int(duration_sec / step_interval)
        
        for i in range(num_steps):
            step_time = i * step_interval
            step_pos = int(step_time * self.SAMPLE_RATE)
            
            time_variation = np.random.uniform(-0.02, 0.02)
            step_pos = max(0, int((step_time + time_variation) * self.SAMPLE_RATE))
            
            volume_variation = np.random.uniform(0.85, 1.15)
            sample_varied = footstep_sample * volume_variation * volume
            
            end_pos = min(step_pos + len(sample_varied), num_samples)
            sample_len = end_pos - step_pos
            
            if sample_len > 0:
                output[step_pos:end_pos] += sample_varied[:sample_len]
        
        return output
    
    def generate_room_tone(
        self,
        duration_sec: float,
        style: str = "villa",
        volume: float = 0.3
    ) -> np.ndarray:
        """
        Génère l'ambiance "Room Tone" de villa luxueuse.
        
        Caractéristiques:
        - Silence habité (pas de bruit de route)
        - Léger souffle de ventilation haut de gamme
        - Occasionnels sons extérieurs étouffés
        
        Args:
            duration_sec: Durée en secondes
            style: Style d'ambiance (villa, modern)
            volume: Volume relatif [0, 1]
            
        Returns:
            Array numpy float32
        """
        num_samples = int(duration_sec * self.SAMPLE_RATE)
        
        pink_noise = self._generate_pink_noise(num_samples) * 0.02
        
        sample_key = f"room_tone_{style}"
        room_sample = self._load_sample(sample_key)
        
        if room_sample is not None:
            room_looped = np.tile(room_sample, int(np.ceil(num_samples / len(room_sample))))
            room_looped = room_looped[:num_samples]
            output = pink_noise + room_looped * volume
        else:
            self._log(f"   ⚠️ Room tone {style} non trouvé, fallback synthétique")
            output = pink_noise * volume
            
            t = np.linspace(0, duration_sec, num_samples)
            low_rumble = np.sin(2 * np.pi * 30 * t) * 0.01
            output += low_rumble
            
            ac_drone = np.sin(2 * np.pi * 60 * t) * 0.005
            output += ac_drone
        
        return output
    
    def generate_cloth_rustle(
        self,
        duration_sec: float,
        intensity: str = "subtle",
        volume: float = 0.2
    ) -> np.ndarray:
        """
        Génère des froissements de vêtements POV.
        
        Synchronisé avec les mouvements de caméra pour renforcer
        l'illusion que c'est filmé par quelqu'un qui marche.
        
        Args:
            duration_sec: Durée en secondes
            intensity: Intensité (subtle, moderate, active)
            volume: Volume relatif [0, 1]
            
        Returns:
            Array numpy float32
        """
        num_samples = int(duration_sec * self.SAMPLE_RATE)
        output = np.zeros(num_samples, dtype=np.float32)
        
        rustle_freq = {"subtle": 0.3, "moderate": 0.6, "active": 1.0}.get(intensity, 0.3)
        num_rustles = int(duration_sec * rustle_freq)
        
        rustle_sample = self._load_sample("cloth_rustle")
        
        if rustle_sample is None:
            self._log("   ⚠️ Cloth rustle non trouvé, fallback synthétique")
            rustle_sample = self._generate_synthetic_rustle()
        
        for _ in range(num_rustles):
            if len(rustle_sample) >= num_samples:
                pos = 0
            else:
                pos = np.random.randint(0, num_samples - len(rustle_sample))
            
            variation = np.random.uniform(0.7, 1.3)
            
            end_pos = min(pos + len(rustle_sample), num_samples)
            sample_len = end_pos - pos
            
            if sample_len > 0:
                output[pos:end_pos] += rustle_sample[:sample_len] * variation * volume
        
        return output
    
    def generate_breathing(
        self,
        duration_sec: float,
        cycle_sec: float = HANDHELD_BREATHING_CYCLE,
        volume: float = 0.15
    ) -> np.ndarray:
        """
        Génère une respiration subtile synchronisée avec le breathing zoom.
        
        La respiration suit le même cycle que le breathing zoom de la caméra (4s)
        pour renforcer l'illusion d'une personne réelle filmant.
        
        Args:
            duration_sec: Durée en secondes
            cycle_sec: Cycle respiratoire (synced avec camera breathing)
            volume: Volume relatif [0, 1]
            
        Returns:
            Array numpy float32
        """
        num_samples = int(duration_sec * self.SAMPLE_RATE)
        
        t = np.linspace(0, duration_sec, num_samples)
        breathing_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * t / cycle_sec)
        
        noise = np.random.randn(num_samples).astype(np.float32) * 0.01
        
        window_size = int(self.SAMPLE_RATE / 100)
        if window_size > 0:
            kernel = np.ones(window_size) / window_size
            filtered = np.convolve(noise, kernel, mode='same')
        else:
            filtered = noise
        
        breathing_sample = self._load_sample("breathing_subtle")
        
        if breathing_sample is not None:
            breathing_looped = np.tile(breathing_sample, int(np.ceil(num_samples / len(breathing_sample))))
            breathing_looped = breathing_looped[:num_samples]
            output = breathing_looped * breathing_envelope * volume
        else:
            output = filtered * breathing_envelope * volume
        
        return output.astype(np.float32)
    
    def generate_wind(
        self,
        duration_sec: float,
        intensity: str = "light",
        volume: float = 0.1
    ) -> np.ndarray:
        """
        Génère un léger son de vent/courant d'air.
        
        Args:
            duration_sec: Durée en secondes
            intensity: Intensité (light, moderate)
            volume: Volume relatif [0, 1]
            
        Returns:
            Array numpy float32
        """
        num_samples = int(duration_sec * self.SAMPLE_RATE)
        
        wind_sample = self._load_sample("wind_light")
        
        if wind_sample is not None:
            wind_looped = np.tile(wind_sample, int(np.ceil(num_samples / len(wind_sample))))
            wind_looped = wind_looped[:num_samples]
            
            t = np.linspace(0, duration_sec, num_samples)
            modulation = 0.7 + 0.3 * np.sin(2 * np.pi * t / 8.0)
            
            return (wind_looped * modulation * volume).astype(np.float32)
        else:
            pink = self._generate_pink_noise(num_samples)
            
            t = np.linspace(0, duration_sec, num_samples)
            modulation = 0.6 + 0.4 * np.sin(2 * np.pi * t / 10.0)
            
            return (pink * modulation * volume * 0.3).astype(np.float32)
    
    def _generate_pink_noise(self, num_samples: int) -> np.ndarray:
        """
        Génère du bruit rose (1/f).
        
        Le bruit rose a plus d'énergie dans les basses fréquences,
        ce qui le rend plus naturel pour l'ambiance.
        
        Args:
            num_samples: Nombre d'échantillons
            
        Returns:
            Array numpy float32
        """
        white = np.random.randn(num_samples).astype(np.float32)
        
        b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786], dtype=np.float32)
        a = np.array([1.0, -2.494956002, 2.017265875, -0.522189400], dtype=np.float32)
        
        pink = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(4, num_samples):
            pink[i] = (b[0]*white[i] + b[1]*white[i-1] + b[2]*white[i-2] + b[3]*white[i-3]
                      - a[1]*pink[i-1] - a[2]*pink[i-2] - a[3]*pink[i-3])
        
        return pink
    
    def _generate_synthetic_footstep(self) -> np.ndarray:
        """
        Fallback: génère un pas synthétique.
        
        Combine:
        - Impact basse fréquence
        - Click haute fréquence
        - Decay rapide
        
        Returns:
            Array numpy float32 (~0.15s)
        """
        duration = 0.15
        num_samples = int(duration * self.SAMPLE_RATE)
        t = np.linspace(0, duration, num_samples)
        
        impact = np.exp(-t * 30) * np.sin(2 * np.pi * 80 * t)
        
        click = np.exp(-t * 50) * np.random.randn(num_samples) * 0.3
        
        mids = np.exp(-t * 20) * np.sin(2 * np.pi * 200 * t) * 0.2
        
        return (impact + click + mids).astype(np.float32) * 0.5
    
    def _generate_synthetic_rustle(self) -> np.ndarray:
        """
        Fallback: génère un froissement synthétique.
        
        Bruit filtré avec envelope exponentielle.
        
        Returns:
            Array numpy float32 (~0.3s)
        """
        duration = 0.3
        num_samples = int(duration * self.SAMPLE_RATE)
        
        noise = np.random.randn(num_samples).astype(np.float32)
        
        envelope = np.exp(-np.linspace(0, 5, num_samples))
        
        window_size = 10
        kernel = np.ones(window_size) / window_size
        filtered = np.convolve(noise, kernel, mode='same')
        
        return (filtered * envelope * 0.1).astype(np.float32)


def generate_asmr_track(
    duration_sec: float,
    assetshub_path: str,
    include_footsteps: bool = True,
    include_room_tone: bool = True,
    include_cloth: bool = True,
    include_breathing: bool = True,
    walking_freq_hz: float = HANDHELD_Z_FREQ,
    breathing_cycle_sec: float = HANDHELD_BREATHING_CYCLE
) -> Dict[str, np.ndarray]:
    """
    Fonction helper pour générer toutes les pistes ASMR.
    
    Args:
        duration_sec: Durée en secondes
        assetshub_path: Chemin vers ASSETSHUB
        include_*: Activer/désactiver chaque couche
        walking_freq_hz: Fréquence des pas
        breathing_cycle_sec: Cycle de respiration
        
    Returns:
        Dict avec les pistes audio par nom
    """
    synth = ASMRSynthesizer(assetshub_path)
    tracks = {}
    
    if include_footsteps:
        tracks["footsteps"] = synth.generate_footsteps_track(
            duration_sec,
            walking_freq_hz=walking_freq_hz
        )
    
    if include_room_tone:
        tracks["room_tone"] = synth.generate_room_tone(duration_sec)
    
    if include_cloth:
        tracks["cloth"] = synth.generate_cloth_rustle(duration_sec)
    
    if include_breathing:
        tracks["breathing"] = synth.generate_breathing(
            duration_sec,
            cycle_sec=breathing_cycle_sec
        )
    
    return tracks


if __name__ == "__main__":
    print("=" * 60)
    print("🎵 ASMR SYNTHESIZER - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   SAMPLE_RATE: {SAMPLE_RATE} Hz")
    print(f"   HANDHELD_Z_FREQ: {HANDHELD_Z_FREQ} Hz (~{int(HANDHELD_Z_FREQ * 60)} pas/min)")
    print(f"   HANDHELD_BREATHING_CYCLE: {HANDHELD_BREATHING_CYCLE}s")
    print(f"   SCIPY_AVAILABLE: {SCIPY_AVAILABLE}")
    
    print(f"\n📋 Samples configurés:")
    for key, path in SAMPLE_PATHS.items():
        print(f"   {key}: {path}")
    
    print(f"\n🔧 Test génération synthétique:")
    synth = ASMRSynthesizer("/tmp/assetshub_test", verbose=True)
    
    footstep = synth._generate_synthetic_footstep()
    print(f"   ✓ Footstep synthétique: {len(footstep)} samples ({len(footstep)/SAMPLE_RATE:.3f}s)")
    
    rustle = synth._generate_synthetic_rustle()
    print(f"   ✓ Rustle synthétique: {len(rustle)} samples ({len(rustle)/SAMPLE_RATE:.3f}s)")
    
    duration = 5.0
    print(f"\n🔧 Test pistes ({duration}s):")
    
    footsteps = synth.generate_footsteps_track(duration)
    print(f"   ✓ Footsteps: {len(footsteps)} samples")
    
    room = synth.generate_room_tone(duration)
    print(f"   ✓ Room tone: {len(room)} samples")
    
    cloth = synth.generate_cloth_rustle(duration)
    print(f"   ✓ Cloth rustle: {len(cloth)} samples")
    
    breathing = synth.generate_breathing(duration)
    print(f"   ✓ Breathing: {len(breathing)} samples")
    
    print("\n✅ Module asmr_synthesizer.py fonctionnel")
