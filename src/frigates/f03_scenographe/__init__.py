"""
EXODUS-SPECULUM - Frégate SCÉNOGRAPHE
Génération géométrie 3D via Blender Python (BPY).

Ce module crée la coquille architecturale:
- RoomBuilder: Génère les 6 surfaces de la pièce avec displacement
- ProxyGenerator: Crée les proxies Ghost pour les meubles
- OpeningCutter: Perce les ouvertures (portes/fenêtres)
- run_scenographe_pipeline: Orchestrateur complet
"""

from .room_builder import RoomBuilder
from .proxy_generator import ProxyGenerator
from .opening_cutter import OpeningCutter
from .scenographe_pipeline import ScenographePipeline, run_scenographe_pipeline

__all__ = [
    'RoomBuilder',
    'ProxyGenerator',
    'OpeningCutter',
    'ScenographePipeline',
    'run_scenographe_pipeline',
]
