#!/usr/bin/env python3
"""
FRIGATE_04_LOGISTIQUE - Asset replacement
Ghost Proxy → Real 3D Assets via Library Linking.
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
