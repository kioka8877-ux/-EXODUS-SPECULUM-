"""
FRIGATE_04_LOGISTIQUE - Asset Replacement
Ghost Proxy → Real 3D Assets via Blender Linked Libraries
"""

from .logistique_pipeline import LogistiquePipeline
from .ghost_detector import GhostDetector
from .asset_matcher import AssetMatcher
from .library_linker import LibraryLinker
from .lod_manager import LODManager

__all__ = [
    'LogistiquePipeline',
    'GhostDetector',
    'AssetMatcher',
    'LibraryLinker',
    'LODManager',
]
