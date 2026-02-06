"""
EXODUS-SPECULUM - Frégates
Pipeline de transformation vidéo → 3D.
"""

try:
    from . import f00_cortex
except ImportError:
    f00_cortex = None

try:
    from . import f01_scanner
except ImportError:
    f01_scanner = None

try:
    from . import f03_scenographe
except ImportError:
    f03_scenographe = None

try:
    from . import f04_projectionniste
except ImportError:
    f04_projectionniste = None

try:
    from . import f05_logistique
except ImportError:
    f05_logistique = None

try:
    from . import f06_directeur_photo
except ImportError:
    f06_directeur_photo = None

try:
    from . import f07_alchimiste
except ImportError:
    f07_alchimiste = None

try:
    from . import f08_porte_avions
except ImportError:
    f08_porte_avions = None

__all__ = [
    'f00_cortex',
    'f01_scanner',
    'f03_scenographe',
    'f04_projectionniste',
    'f05_logistique',
    'f06_directeur_photo',
    'f07_alchimiste',
    'f08_porte_avions',
]
