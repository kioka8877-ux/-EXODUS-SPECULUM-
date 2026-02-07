#!/usr/bin/env python3
"""
FRIGATE_05_DIRECTEUR_PHOTO - Camera animation + Smart-Crop
Animation caméra humanisée et adaptation multi-format.
"""

from .directeur_pipeline import DirecteurPipeline
from .camera_humanizer import CameraHumanizer
from .format_adapter import FormatAdapter
from .smart_crop import SmartCrop
from .shakify import Shakify

__all__ = [
    'DirecteurPipeline',
    'CameraHumanizer',
    'FormatAdapter',
    'SmartCrop',
    'Shakify',
]
