"""
EXODUS-SPECULUM - Frégate ALCHIMISTE
Pipeline de transmutation: Rendu brut → 4K/60FPS via protocole TURBO-SPECULUM.

Ce module transforme les scènes animées en vidéos haute qualité:
- CyclesRenderer: Configuration Cycles optimisée GPU (T4 Colab)
- ESRGANUpscaler: Real-ESRGAN x4plus pour upscale 4x
- RIFEInterpolator: RIFE v4.6 pour interpolation temporelle
- ChunkProcessor: Streaming pipeline anti-goulot (15GB Drive limit)
- AlchimistePipeline: Orchestrateur complet du workflow

Philosophie: Du Plomb à l'Or
Render low-res → ESRGAN 4x → RIFE interpolation = 4K/60FPS sans la VRAM d'un rendu natif.

Protocole TURBO-SPECULUM:
- ÉCLAIREUR: 540p/16 samples/12fps → 540p/12fps (preview)
- CONQUÉRANT: 1080p/32 samples/24fps → ESRGAN → RIFE → 4K/60fps
- SOUVERAIN: 4K/128 samples/60fps → 4K/60fps (rendu natif)

Constantes:
- TURBO_MODES: Configurations des trois modes
- CHUNK_SIZE_FRAMES: 120 frames par chunk (~5s à 24fps)
- CLEANUP_TEMP_FILES: True (libère le disque)

Usage:
    from src.frigates.f07_alchimiste import run_alchimiste_pipeline
    
    result = run_alchimiste_pipeline(
        scene_animated_path="/path/to/scene_animated.blend",
        project_id="mon_projet",
        turbo_mode="conquerant"  # Mode alchimiste optimal
    )
"""

from .cycles_renderer import (
    CyclesRenderer,
    TURBO_MODES
)
from .esrgan_upscaler import (
    ESRGANUpscaler,
    ESRGAN_BINARY,
    ESRGAN_MODEL,
    ESRGAN_SCALE_FACTOR,
    ESRGAN_MODELS
)
from .rife_interpolator import (
    RIFEInterpolator,
    RIFE_BINARY,
    RIFE_MODEL,
    RIFE_MODELS,
    INTERPOLATION_PRESETS
)
from .chunk_processor import (
    ChunkProcessor,
    CHUNK_SIZE_FRAMES,
    CLEANUP_TEMP_FILES
)
from .alchimiste_pipeline import (
    AlchimistePipeline,
    run_alchimiste_pipeline,
    EXODUS_VERSION
)

__all__ = [
    'CyclesRenderer',
    'ESRGANUpscaler',
    'RIFEInterpolator',
    'ChunkProcessor',
    'AlchimistePipeline',
    'run_alchimiste_pipeline',
    'TURBO_MODES',
    'ESRGAN_BINARY',
    'ESRGAN_MODEL',
    'ESRGAN_SCALE_FACTOR',
    'ESRGAN_MODELS',
    'RIFE_BINARY',
    'RIFE_MODEL',
    'RIFE_MODELS',
    'INTERPOLATION_PRESETS',
    'CHUNK_SIZE_FRAMES',
    'CLEANUP_TEMP_FILES',
    'EXODUS_VERSION',
]

__version__ = "0.7.0"
__frigate__ = "F07_ALCHIMISTE"
