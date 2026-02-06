"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS
Pipeline d'assemblage final: Vidéo + Sound Design ASMR → Export multi-plateformes.

Ce module transforme les rendus F07 en produits finaux immersifs:
- FFmpegEncoder: Encodage vidéo H.264/H.265 haute qualité
- ASMRSynthesizer: Sound Design ASMR (pas, ambiance, froissements, respiration)
- AudioMixer: Mixage multi-pistes avec normalisation
- MetadataInjector: Anti-shadowban via métadonnées uniques
- FormatExporter: Export multi-plateformes (YouTube/TikTok/Instagram)
- PorteAvionsPipeline: Orchestrateur complet du workflow

Philosophie: L'Immersion Sensorielle
Transformer une vidéo 3D en "vraie visite filmée à l'iPhone" via un sound design
ASMR qui renforce l'illusion de présence humaine.

Synchronisation Camera-Audio:
- Pas synchronisés avec HANDHELD_Z_FREQ (1.8 Hz = walking bounce)
- Respiration synchronisée avec HANDHELD_BREATHING_CYCLE (4s)

Constantes:
- CODEC_PROFILES: Configurations d'encodage (quality, compatibility, fast)
- PLATFORM_SPECS: Spécifications par plateforme (YouTube, TikTok, Instagram)
- SAMPLE_RATE: 48000 Hz (standard vidéo)
- ASMR_DEFAULTS: Volumes par défaut des couches audio

Usage:
    from src.frigates.f08_porte_avions import run_porte_avions_pipeline
    
    result = run_porte_avions_pipeline(
        video_input="/path/to/temp_render.mp4",
        project_id="villa_monaco",
        export_platforms=["youtube_4k", "tiktok", "instagram_reels"]
    )
"""

from .ffmpeg_encoder import (
    FFmpegEncoder,
    CODEC_PROFILES
)
from .asmr_synthesizer import (
    ASMRSynthesizer,
    generate_asmr_track,
    SAMPLE_RATE,
    HANDHELD_Z_FREQ,
    HANDHELD_BREATHING_CYCLE,
    SAMPLE_PATHS
)
from .audio_mixer import (
    AudioMixer,
    LIMITER_THRESHOLD
)
from .metadata_injector import (
    MetadataInjector,
    ANTI_FINGERPRINT_PARAMS
)
from .format_exporter import (
    FormatExporter,
    PLATFORM_SPECS
)
from .porte_avions_pipeline import (
    PorteAvionsPipeline,
    run_porte_avions_pipeline,
    EXODUS_VERSION,
    ASMR_DEFAULTS
)

__all__ = [
    'FFmpegEncoder',
    'ASMRSynthesizer',
    'AudioMixer',
    'MetadataInjector',
    'FormatExporter',
    'PorteAvionsPipeline',
    'run_porte_avions_pipeline',
    'generate_asmr_track',
    'CODEC_PROFILES',
    'PLATFORM_SPECS',
    'SAMPLE_RATE',
    'HANDHELD_Z_FREQ',
    'HANDHELD_BREATHING_CYCLE',
    'SAMPLE_PATHS',
    'LIMITER_THRESHOLD',
    'ANTI_FINGERPRINT_PARAMS',
    'ASMR_DEFAULTS',
    'EXODUS_VERSION',
]

__version__ = "0.8.0"
__frigate__ = "F08_PORTE_AVIONS"
