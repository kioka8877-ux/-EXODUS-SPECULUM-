"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO
Camera animation - iPhone POV Humanizer pour tournage style visite d'appartement.

Ce module anime la caméra pour simuler un tournage iPhone tenu à la main,
maximisant l'authenticité et la viralité sur TikTok/Reels.

Philosophie: L'Œil de l'Envie
Recréer le style "Femme qui filme avec son iPhone" pour maximiser
l'authenticité des visites virtuelles d'appartements.

Composants:
- CameraHumanizer: Focale iPhone 26mm + walking bounce + breathing zoom
- Shakify: Bruit de Perlin pour micro-tremblements naturels du poignet
- SmartCrop: POI tracking + sensor shift vers zones d'intérêt
- FormatAdapter: Conversion 16:9 → 9:16 / 1:1 pour TikTok/Reels/YouTube
- DirecteurPipeline: Orchestrateur complet du workflow

Constantes iPhone:
- IPHONE_FOCAL_LENGTH: 26mm (équivalent 24-28mm smartphone)
- HANDHELD_Z_FREQ: 1.8 Hz (fréquence oscillation marche)
- HANDHELD_Z_AMPLITUDE: 0.02m (amplitude bounce)
- HANDHELD_ROT_NOISE: 0.005 rad (bruit rotation XY)
- HANDHELD_BREATHING_CYCLE: 4.0s (cycle respiration)

Usage:
    from src.frigates.f06_directeur_photo import run_directeur_pipeline
    
    result = run_directeur_pipeline(
        scene_furnished_path="/path/to/scene_furnished.blend",
        masterplan_path="/path/to/masterplan.json",
        output_format="VERTICAL",  # TikTok/Reels
        duration_seconds=30.0,
        fps=24
    )
"""

from .camera_humanizer import (
    CameraHumanizer,
    IPHONE_FOCAL_LENGTH,
    HANDHELD_Z_FREQ,
    HANDHELD_Z_AMPLITUDE,
    HANDHELD_ROT_NOISE,
    HANDHELD_BREATHING_CYCLE
)
from .shakify import Shakify
from .smart_crop import SmartCrop, MAX_SENSOR_SHIFT, POI_TRACKING_SMOOTHNESS
from .format_adapter import FormatAdapter, OUTPUT_FORMATS, MAX_ZOOM_FACTOR
from .directeur_pipeline import DirecteurPipeline, run_directeur_pipeline

__all__ = [
    'CameraHumanizer',
    'Shakify',
    'SmartCrop',
    'FormatAdapter',
    'DirecteurPipeline', 'run_directeur_pipeline',
    'IPHONE_FOCAL_LENGTH',
    'HANDHELD_Z_FREQ',
    'HANDHELD_Z_AMPLITUDE',
    'HANDHELD_ROT_NOISE',
    'HANDHELD_BREATHING_CYCLE',
    'MAX_SENSOR_SHIFT',
    'POI_TRACKING_SMOOTHNESS',
    'OUTPUT_FORMATS',
    'MAX_ZOOM_FACTOR',
]

__version__ = "0.6.0"
__frigate__ = "F06_DIRECTEUR_PHOTO"
