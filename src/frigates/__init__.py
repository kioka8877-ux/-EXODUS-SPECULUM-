"""
EXODUS-SPECULUM - Frégates
Pipeline de transformation vidéo → 3D.
"""

try:
    from . import f01_scanner
except ImportError:
    f01_scanner = None

try:
    from . import f00_cortex
except ImportError:
    f00_cortex = None

try:
    from . import f03_scenographe
except ImportError:
    f03_scenographe = None

try:
    from . import f04_projectionniste
except ImportError:
    f04_projectionniste = None

__all__ = ['f01_scanner', 'f00_cortex', 'f03_scenographe', 'f04_projectionniste']
