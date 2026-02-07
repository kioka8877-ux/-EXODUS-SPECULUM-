"""
FRIGATE_02_SCENOGRAPHE - Génération géométrie 3D
Blob room + proxies Ghost via Blender bpy
"""

from .scenographe_pipeline import ScenographePipeline
from .room_builder import RoomBuilder
from .proxy_generator import ProxyGenerator
from .opening_cutter import OpeningCutter

__all__ = [
    'ScenographePipeline',
    'RoomBuilder',
    'ProxyGenerator',
    'OpeningCutter',
]
