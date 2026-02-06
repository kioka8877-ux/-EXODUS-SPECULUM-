"""
EXODUS-SPECULUM - Frégate PROJECTIONNISTE
Camera Projection Mapping pour textures vidéo sur géométrie 3D.

Ce module projette les textures source sur la coquille architecturale:
- CameraSetup: Configure les caméras de projection pour les 3 keyframes
- UVProjector: Gère la projection UV depuis les caméras
- MultiProjectionShader: Crée le matériau multi-projection avec blending animé
- run_projectionniste_pipeline: Orchestrateur complet
"""

from .camera_setup import CameraSetup
from .uv_projector import UVProjector
from .multi_projection_shader import MultiProjectionShader
from .projectionniste_pipeline import ProjectionnistePipeline, run_projectionniste_pipeline

__all__ = [
    'CameraSetup',
    'UVProjector',
    'MultiProjectionShader',
    'ProjectionnistePipeline',
    'run_projectionniste_pipeline',
]
