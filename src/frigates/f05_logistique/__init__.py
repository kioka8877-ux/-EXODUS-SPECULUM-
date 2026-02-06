"""
EXODUS-SPECULUM - Frégate LOGISTIQUE
Asset replacement - Ghost Proxy → Real 3D Assets depuis ASSETSHUB.

Ce module remplace les objets Ghost Proxy (placeholders) par de vrais assets 3D
linkés depuis une bibliothèque externe (ASSETSHUB), avec système LOD dynamique.

Composants:
- GhostDetector: Scanne la scène pour détecter les ghost_proxy=True
- AssetMatcher: Fuzzy matching par type et dimensions
- LibraryLinker: Link (pas Append!) des assets via bpy.data.libraries
- LODManager: Système LOD0/LOD1/LOD2 basé sur distance caméra
- LogistiquePipeline: Orchestrateur complet du workflow

Usage:
    from src.frigates.f05_logistique import run_logistique_pipeline
    
    result = run_logistique_pipeline(
        scene_projected_path="/path/to/scene_projected.blend",
        assetshub_path="/path/to/ASSETSHUB",
        match_threshold=0.7,
        setup_lod=True
    )
"""

from .ghost_detector import GhostDetector, GhostProxy
from .asset_matcher import AssetMatcher, AssetMatch
from .library_linker import LibraryLinker
from .lod_manager import LODManager
from .logistique_pipeline import LogistiquePipeline, run_logistique_pipeline

__all__ = [
    'GhostDetector', 'GhostProxy',
    'AssetMatcher', 'AssetMatch',
    'LibraryLinker',
    'LODManager',
    'LogistiquePipeline', 'run_logistique_pipeline',
]

__version__ = "0.5.0"
__frigate__ = "F05_LOGISTIQUE"
