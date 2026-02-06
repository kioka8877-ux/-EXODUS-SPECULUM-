#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS - Audio Mixer
Mixage multi-pistes audio avec normalisation et limiting.

Ce module combine les différentes couches audio ASMR en une piste finale:
- Mix des volumes individuels
- Normalisation pour éviter le clipping
- Soft limiter pour protection
- Synchronisation avec la durée vidéo

Usage:
    mixer = AudioMixer()
    
    mixed_path = mixer.mix_tracks([
        (footsteps_array, 0.5),
        (room_tone_array, 0.3),
        (cloth_array, 0.2),
        (breathing_array, 0.15)
    ], output_path="/path/to/mix.wav")
"""

import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    wavfile = None

SAMPLE_RATE = 48000
DEFAULT_BIT_DEPTH = 16
LIMITER_THRESHOLD = 0.95


class AudioMixer:
    """
    Mixe les différentes couches audio ASMR en une piste finale.
    
    Features:
    - Mix multi-pistes avec volumes individuels
    - Normalisation automatique
    - Soft limiter (tanh) pour éviter le clipping
    - Export WAV 16/24 bits
    - Synchronisation avec durée vidéo
    
    Usage:
        mixer = AudioMixer()
        
        output_path = mixer.mix_tracks([
            (footsteps, 0.5),   # 50% volume
            (room_tone, 0.3),  # 30% volume
            (cloth, 0.2),      # 20% volume
        ], "/path/to/output.wav")
    """
    
    SAMPLE_RATE = SAMPLE_RATE
    
    def __init__(self, sample_rate: int = SAMPLE_RATE, verbose: bool = True):
        """
        Args:
            sample_rate: Taux d'échantillonnage (défaut: 48000)
            verbose: Affiche les logs détaillés
        """
        self.sample_rate = sample_rate
        self.verbose = verbose
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(message)
    
    def mix_tracks(
        self,
        tracks: List[Tuple[np.ndarray, float]],
        output_path: str,
        normalize: bool = True,
        limiter_threshold: float = LIMITER_THRESHOLD,
        bit_depth: int = DEFAULT_BIT_DEPTH
    ) -> str:
        """
        Mixe plusieurs pistes avec leurs volumes respectifs.
        
        Args:
            tracks: Liste de (audio_array, volume_multiplier)
            output_path: Chemin de sortie .wav
            normalize: Normaliser le mix final
            limiter_threshold: Seuil du limiter (évite clipping)
            bit_depth: Profondeur de bits (16 ou 24)
            
        Returns:
            Chemin du fichier WAV créé
        """
        if not tracks:
            raise ValueError("Au moins une piste requise")
        
        if not SCIPY_AVAILABLE:
            self._log("   ⚠️ scipy non disponible, export WAV impossible")
            return self._fallback_mix(tracks, output_path)
        
        max_len = max(len(t[0]) for t in tracks)
        self._log(f"   🎚️ Mixage de {len(tracks)} pistes ({max_len} samples)")
        
        mix = np.zeros(max_len, dtype=np.float64)
        
        for i, (audio, volume) in enumerate(tracks):
            if len(audio) < max_len:
                padded = np.pad(audio, (0, max_len - len(audio)))
            else:
                padded = audio[:max_len]
            
            mix += padded.astype(np.float64) * volume
            self._log(f"      Track {i+1}: {len(audio)} samples @ {volume:.0%} volume")
        
        if normalize:
            peak = np.max(np.abs(mix))
            if peak > 0:
                mix = mix / peak * limiter_threshold
                self._log(f"   📊 Normalisé (peak: {peak:.3f} → {limiter_threshold:.3f})")
        
        mix = np.tanh(mix * 1.5) / np.tanh(1.5)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if bit_depth == 24:
            audio_int = (mix * 8388607).astype(np.int32)
            wavfile.write(output_path, self.sample_rate, audio_int)
        else:
            audio_int = (mix * 32767).astype(np.int16)
            wavfile.write(output_path, self.sample_rate, audio_int)
        
        self._log(f"   ✓ Mix exporté: {output_path} ({bit_depth} bits)")
        
        return output_path
    
    def _fallback_mix(
        self,
        tracks: List[Tuple[np.ndarray, float]],
        output_path: str
    ) -> str:
        """
        Fallback: sauvegarde le mix en format raw si scipy non disponible.
        
        Args:
            tracks: Liste de pistes
            output_path: Chemin de sortie
            
        Returns:
            Chemin du fichier créé (avec extension .raw)
        """
        max_len = max(len(t[0]) for t in tracks)
        mix = np.zeros(max_len, dtype=np.float32)
        
        for audio, volume in tracks:
            if len(audio) < max_len:
                padded = np.pad(audio, (0, max_len - len(audio)))
            else:
                padded = audio[:max_len]
            mix += padded * volume
        
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.95
        
        raw_path = output_path.replace(".wav", ".raw")
        mix.astype(np.float32).tofile(raw_path)
        
        self._log(f"   ⚠️ Fallback: exporté en raw float32: {raw_path}")
        return raw_path
    
    def sync_to_video(
        self,
        audio_path: str,
        video_duration_sec: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Ajuste la durée audio pour matcher la vidéo.
        
        Args:
            audio_path: Chemin du fichier audio
            video_duration_sec: Durée de la vidéo en secondes
            output_path: Chemin de sortie (défaut: audio_path avec _synced)
            
        Returns:
            Chemin du fichier synchronisé
        """
        if not SCIPY_AVAILABLE:
            self._log("   ⚠️ scipy non disponible")
            return audio_path
        
        sr, audio = wavfile.read(audio_path)
        
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        elif audio.dtype == np.int32:
            audio = audio.astype(np.float32) / 2147483648.0
        
        audio_duration = len(audio) / sr
        
        if abs(audio_duration - video_duration_sec) < 0.1:
            self._log(f"   ✓ Audio déjà synchronisé ({audio_duration:.2f}s ≈ {video_duration_sec:.2f}s)")
            return audio_path
        
        target_samples = int(video_duration_sec * sr)
        
        if len(audio) > target_samples:
            audio = audio[:target_samples]
            self._log(f"   ✂️ Audio tronqué: {audio_duration:.2f}s → {video_duration_sec:.2f}s")
        else:
            padding = target_samples - len(audio)
            audio = np.pad(audio, (0, padding))
            self._log(f"   📏 Audio étendu: {audio_duration:.2f}s → {video_duration_sec:.2f}s")
        
        if output_path is None:
            output_path = audio_path.replace(".wav", "_synced.wav")
        
        audio_int = (audio * 32767).astype(np.int16)
        wavfile.write(output_path, sr, audio_int)
        
        return output_path
    
    def apply_fade(
        self,
        audio: np.ndarray,
        fade_in_sec: float = 0.5,
        fade_out_sec: float = 1.0
    ) -> np.ndarray:
        """
        Applique un fade in/out à l'audio.
        
        Args:
            audio: Array audio
            fade_in_sec: Durée du fade in en secondes
            fade_out_sec: Durée du fade out en secondes
            
        Returns:
            Audio avec fades appliqués
        """
        audio = audio.copy()
        
        fade_in_samples = int(fade_in_sec * self.sample_rate)
        fade_out_samples = int(fade_out_sec * self.sample_rate)
        
        if fade_in_samples > 0 and fade_in_samples < len(audio):
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            audio[:fade_in_samples] *= fade_in_curve
        
        if fade_out_samples > 0 and fade_out_samples < len(audio):
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            audio[-fade_out_samples:] *= fade_out_curve
        
        return audio
    
    def create_stereo(
        self,
        mono_audio: np.ndarray,
        pan: float = 0.0
    ) -> np.ndarray:
        """
        Convertit mono en stéréo avec panoramique optionnel.
        
        Args:
            mono_audio: Audio mono
            pan: Panoramique [-1 (gauche), 0 (centre), 1 (droite)]
            
        Returns:
            Audio stéréo (N, 2)
        """
        left_gain = np.sqrt(0.5 * (1 - pan))
        right_gain = np.sqrt(0.5 * (1 + pan))
        
        stereo = np.zeros((len(mono_audio), 2), dtype=mono_audio.dtype)
        stereo[:, 0] = mono_audio * left_gain
        stereo[:, 1] = mono_audio * right_gain
        
        return stereo
    
    def get_audio_stats(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Calcule les statistiques d'un signal audio.
        
        Args:
            audio: Array audio
            
        Returns:
            Dict avec peak, RMS, durée, etc.
        """
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio ** 2))
        duration = len(audio) / self.sample_rate
        
        db_peak = 20 * np.log10(peak) if peak > 0 else -np.inf
        db_rms = 20 * np.log10(rms) if rms > 0 else -np.inf
        
        return {
            "samples": len(audio),
            "duration_sec": duration,
            "peak": peak,
            "peak_db": db_peak,
            "rms": rms,
            "rms_db": db_rms,
            "crest_factor": peak / rms if rms > 0 else 0
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🎚️ AUDIO MIXER - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   SAMPLE_RATE: {SAMPLE_RATE} Hz")
    print(f"   DEFAULT_BIT_DEPTH: {DEFAULT_BIT_DEPTH} bits")
    print(f"   LIMITER_THRESHOLD: {LIMITER_THRESHOLD}")
    print(f"   SCIPY_AVAILABLE: {SCIPY_AVAILABLE}")
    
    print(f"\n🔧 Test génération:")
    mixer = AudioMixer(verbose=True)
    
    duration = 2.0
    num_samples = int(duration * SAMPLE_RATE)
    
    t = np.linspace(0, duration, num_samples)
    sine_440 = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    sine_880 = (np.sin(2 * np.pi * 880 * t) * 0.3).astype(np.float32)
    noise = (np.random.randn(num_samples) * 0.1).astype(np.float32)
    
    print(f"\n📊 Statistiques pistes:")
    for name, audio in [("Sine 440Hz", sine_440), ("Sine 880Hz", sine_880), ("Noise", noise)]:
        stats = mixer.get_audio_stats(audio)
        print(f"   {name}: peak={stats['peak']:.3f} ({stats['peak_db']:.1f}dB), RMS={stats['rms']:.3f}")
    
    print(f"\n🔧 Test fade:")
    faded = mixer.apply_fade(sine_440, fade_in_sec=0.1, fade_out_sec=0.2)
    print(f"   ✓ Fade appliqué: {len(faded)} samples")
    
    print(f"\n🔧 Test stéréo:")
    stereo = mixer.create_stereo(sine_440, pan=-0.5)
    print(f"   ✓ Stéréo créé: shape {stereo.shape}")
    
    print("\n✅ Module audio_mixer.py fonctionnel")
