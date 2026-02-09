#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Output Contracts (Phase 2.5A)
Définit les contrats de sortie pour chaque frégate du pipeline.

Ces contrats spécifient:
- Les formats de fichiers attendus
- Les contraintes de qualité
- Les limites de ressources
- Les profils de livraison

Usage:
    from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS, DELIVERY_PROFILES
"""

from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════
# DELIVERY PROFILES (Modes de rendu)
# ═══════════════════════════════════════════════════════════════════════════

DELIVERY_PROFILES: Dict[str, Dict[str, Any]] = {
    "ECLAIREUR": {
        "description": "Mode rapide pour tests et previews",
        "resolution": (960, 540),
        "fps": 12,
        "samples": 16,
        "denoiser": "OPENIMAGEDENOISE",
        "upscale": False,
        "quality_preset": "preview",
    },
    "CONQUERANT": {
        "description": "Mode production standard",
        "resolution": (1920, 1080),
        "fps": 24,
        "samples": 64,
        "denoiser": "OPTIX",
        "upscale": True,
        "upscale_factor": 2,
        "quality_preset": "production",
    },
    "PREMIUM": {
        "description": "Mode haute qualité pour exports finaux",
        "resolution": (3840, 2160),
        "fps": 60,
        "samples": 128,
        "denoiser": "OPTIX",
        "upscale": True,
        "upscale_factor": 2,
        "interpolation": True,
        "quality_preset": "premium",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# FRIGATE CONTRACTS (Contrats par frégate)
# ═══════════════════════════════════════════════════════════════════════════

FRIGATE_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "F00_CORTEX": {
        "name": "CORTEX - Intelligence IA",
        "inputs": {
            "keyframes": {"type": "image", "format": ["png", "jpg"], "min_count": 1},
        },
        "outputs": {
            "masterplan.json": {
                "type": "json",
                "required_keys": ["project_id", "rooms", "camera_path"],
                "schema_version": "1.0",
            },
        },
        "constraints": {
            "api_calls_per_minute": 60,
            "max_image_size_mb": 10,
            "timeout_seconds": 120,
        },
    },
    "F01_SCANNER": {
        "name": "SCANNER - Extraction & Depth",
        "inputs": {
            "video": {"type": "video", "format": ["mp4", "mov", "avi"]},
        },
        "outputs": {
            "frames/": {
                "type": "directory",
                "content": "image",
                "format": "png",
                "naming": "frame_{:06d}.png",
            },
            "depth_maps/": {
                "type": "directory",
                "content": "depth",
                "format": "png",
                "bit_depth": 16,
                "dtype": "uint16",
                "naming": "depth_{:06d}.png",
            },
            "spatial_data.json": {
                "type": "json",
                "required_keys": ["frames", "detections"],
            },
        },
        "constraints": {
            "max_vram_gb": 12,
            "depth_value_range": [0, 65535],
            "min_resolution": [480, 270],
            "max_resolution": [7680, 4320],
        },
    },
    "F02_SCENOGRAPHE": {
        "name": "SCÉNOGRAPHE - Géométrie 3D",
        "inputs": {
            "masterplan.json": {"type": "json"},
            "depth_maps/": {"type": "directory"},
        },
        "outputs": {
            "scene_shell.blend": {
                "type": "blender",
                "required_collections": ["ROOM_SHELL", "PROXIES"],
                "metadata_embedded": True,
            },
        },
        "constraints": {
            "max_vertices": 500000,
            "max_proxies": 100,
        },
    },
    "F03_PROJECTIONNISTE": {
        "name": "PROJECTIONNISTE - Camera Projection",
        "inputs": {
            "scene_shell.blend": {"type": "blender"},
            "frames/": {"type": "directory"},
        },
        "outputs": {
            "scene_projected.blend": {
                "type": "blender",
                "required_materials": ["ProjectionMaterial"],
                "uv_layers_required": True,
            },
        },
        "constraints": {
            "max_keyframes": 10,
            "texture_resolution_max": 4096,
        },
    },
    "F04_LOGISTIQUE": {
        "name": "LOGISTIQUE - Asset Replacement",
        "inputs": {
            "scene_projected.blend": {"type": "blender"},
            "ASSETSHUB/": {"type": "directory"},
        },
        "outputs": {
            "scene_furnished.blend": {
                "type": "blender",
                "linked_assets": True,
                "lod_enabled": True,
            },
        },
        "constraints": {
            "max_linked_assets": 50,
            "lod_levels": 3,
        },
    },
    "F05_DIRECTEUR_PHOTO": {
        "name": "DIRECTEUR PHOTO - Camera Animation",
        "inputs": {
            "scene_furnished.blend": {"type": "blender"},
        },
        "outputs": {
            "scene_animated.blend": {
                "type": "blender",
                "camera_animated": True,
                "sensor_shift_enabled": True,
            },
        },
        "constraints": {
            "handheld_amplitude_max": 0.02,
            "breathing_amplitude_max": 0.005,
        },
    },
    "F06_ALCHIMISTE": {
        "name": "ALCHIMISTE - Rendu & Upscaling",
        "inputs": {
            "scene_animated.blend": {"type": "blender"},
        },
        "outputs": {
            "rendered_frames/": {
                "type": "directory",
                "content": "image",
                "format": "png",
                "bit_depth": 16,
            },
            "upscaled_frames/": {
                "type": "directory",
                "content": "image",
                "format": "png",
                "optional": True,
            },
        },
        "constraints": {
            "max_vram_gb": 14,
            "samples_range": [16, 256],
            "upscale_models": ["realesrgan-x4plus", "realesrgan-x4plus-anime"],
            "interpolation_models": ["rife-v4"],
        },
    },
    "F07_PORTE_AVIONS": {
        "name": "PORTE-AVIONS - Assemblage Final",
        "inputs": {
            "rendered_frames/": {"type": "directory"},
            "upscaled_frames/": {"type": "directory", "optional": True},
        },
        "outputs": {
            "final_video.mp4": {
                "type": "video",
                "codec": "h264",
                "container": "mp4",
                "audio_codec": "aac",
            },
            "variants/": {
                "type": "directory",
                "content": "video",
                "platforms": ["youtube", "instagram", "tiktok"],
            },
        },
        "constraints": {
            "codec_options": ["h264", "hevc"],
            "fps_range": [12, 60],
            "bitrate_mbps_range": [5, 100],
            "audio_sample_rate": 44100,
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL LIMITS (Limites système globales)
# ═══════════════════════════════════════════════════════════════════════════

GLOBAL_LIMITS: Dict[str, Any] = {
    "max_chunk_transfer_mb": 500,
    "max_total_pipeline_time_hours": 6,
    "max_temp_storage_gb": 100,
    "gpu_memory_threshold_gb": 14,
    "cpu_memory_threshold_gb": 32,
    "max_concurrent_processes": 4,
    "checkpoint_interval_minutes": 15,
}

# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def validate_output(frigate_id: str, output_name: str, output_data: Any) -> tuple[bool, list]:
    """
    Valide une sortie contre son contrat.
    
    Args:
        frigate_id: ID de la frégate (ex: "F01_SCANNER")
        output_name: Nom de la sortie (ex: "depth_maps/")
        output_data: Données ou chemin à valider
        
    Returns:
        (is_valid, errors): Tuple (bool, list of error strings)
    """
    errors = []
    
    if frigate_id not in FRIGATE_CONTRACTS:
        errors.append(f"Unknown frigate: {frigate_id}")
        return False, errors
    
    contract = FRIGATE_CONTRACTS[frigate_id]
    if output_name not in contract.get("outputs", {}):
        errors.append(f"Unknown output: {output_name} for {frigate_id}")
        return False, errors
    
    return len(errors) == 0, errors


def get_profile_config(profile_name: str) -> Dict[str, Any]:
    """
    Récupère la configuration d'un profil de livraison.
    
    Args:
        profile_name: Nom du profil (ECLAIREUR, CONQUERANT, PREMIUM)
        
    Returns:
        Configuration du profil ou config ECLAIREUR par défaut
    """
    return DELIVERY_PROFILES.get(profile_name.upper(), DELIVERY_PROFILES["ECLAIREUR"])


__all__ = [
    "DELIVERY_PROFILES",
    "FRIGATE_CONTRACTS", 
    "GLOBAL_LIMITS",
    "validate_output",
    "get_profile_config",
]
