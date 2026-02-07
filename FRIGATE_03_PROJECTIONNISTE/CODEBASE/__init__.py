#!/usr/bin/env python3
"""
FRIGATE_03_PROJECTIONNISTE - Camera Projection Mapping
Textures vidéo projetées sur géométrie 3D.
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
