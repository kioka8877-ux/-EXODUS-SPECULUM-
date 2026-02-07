"""
FRIGATE_03_PROJECTIONNISTE - Camera Projection Mapping
Projection textures vidéo sur géométrie 3D
"""

from .projectionniste_pipeline import ProjectionnistePipeline
from .camera_setup import CameraSetup
from .uv_projector import UVProjector
from .multi_projection_shader import MultiProjectionShader

__all__ = [
    'ProjectionnistePipeline',
    'CameraSetup',
    'UVProjector',
    'MultiProjectionShader',
]
