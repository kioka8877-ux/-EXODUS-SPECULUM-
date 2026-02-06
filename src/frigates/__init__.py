"""
EXODUS-SPECULUM - Frégates
Pipeline de transformation vidéo → 3D.
"""

from . import f01_scanner
from . import f00_cortex
from . import f03_scenographe

__all__ = ['f01_scanner', 'f00_cortex', 'f03_scenographe']
