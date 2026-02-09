#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Contrats de Sortie par Frégate
Définit les limites de poids et formats pour chaque étape du pipeline.

PROTOCOLE:
- Chaque frégate DOIT valider ses outputs contre ces contrats
- Dépassement = erreur bloquante (pas de warning silencieux)
- Compatible avec structure Drive définie dans paths.py
"""

from CORE_CONFIG.paths import (
    F00_OUTPUT, F01_OUTPUT, F02_OUTPUT, F03_OUTPUT,
    F04_OUTPUT, F05_OUTPUT, F06_OUTPUT, F07_OUTPUT
)

# ============================================================================
# PROFILS DE LIVRAISON FINALE (F07 → Client)
# ============================================================================

DELIVERY_PROFILES = {
    "STANDARD": {
        "name": "SPECULUM_STANDARD",
        "resolution": (1920, 1080),
        "fps": 24,
        "bitrate_mbps": 10,
        "codec": "h264",
        "profile": "high",
        "audio_codec": "aac",
        "audio_bitrate_kbps": 192,
        "target_mb_per_min": 80,
        "tolerance_percent": 15,
    },
    "PREMIUM": {
        "name": "SPECULUM_PREMIUM",
        "resolution": (1920, 1080),
        "fps": 60,
        "bitrate_mbps": 13,
        "codec": "h264",
        "profile": "high",
        "audio_codec": "aac",
        "audio_bitrate_kbps": 192,
        "target_mb_per_min": 100,
        "tolerance_percent": 15,
    },
    "VERTICAL": {
        "name": "SPECULUM_VERTICAL",
        "resolution": (1080, 1920),
        "fps": 30,
        "bitrate_mbps": 10,
        "codec": "h264",
        "profile": "high",
        "audio_codec": "aac",
        "audio_bitrate_kbps": 192,
        "target_mb_per_min": 80,
        "tolerance_percent": 15,
    },
}

# ============================================================================
# CONTRATS PAR FRÉGATE (Processing intermédiaire)
# ============================================================================

FRIGATE_CONTRACTS = {
    "F00_CORTEX": {
        "input": {
            "frames_per_analysis": 5,
            "max_mb_per_request": 10,
        },
        "output": {
            "masterplan": {
                "format": "json",
                "max_kb": 500,
                "required_keys": ["project_id", "rooms", "camera_path"],
            },
        },
        "output_path": F00_OUTPUT,
    },

    "F01_SCANNER": {
        "input": {
            "video_max_mb": 500,
            "video_min_resolution": (720, 480),
        },
        "output": {
            "depth": {
                "format": "npz_compressed",
                "dtype": "uint16",
                "max_mb_per_frame": 2,
                "max_mb_per_chunk_10s": 25,
            },
            "frames": {
                "format": "webp",
                "quality": 92,
                "max_mb_per_frame": 0.5,
                "max_mb_per_chunk_10s": 20,
            },
        },
        "chunk_duration_sec": 10,
        "chunk_max_mb": 60,
        "output_path": F01_OUTPUT,
    },

    "F02_SCENOGRAPHE": {
        "input": {"masterplan_max_kb": 500},
        "output": {
            "blend": {
                "format": "blend",
                "max_mb": 50,
                "max_vertices": 500_000,
                "max_objects": 200,
            },
        },
        "output_path": F02_OUTPUT,
    },

    "F03_PROJECTIONNISTE": {
        "input": {"blend_max_mb": 50},
        "output": {
            "blend": {
                "format": "blend",
                "max_mb": 60,
            },
        },
        "output_path": F03_OUTPUT,
    },

    "F04_LOGISTIQUE": {
        "input": {"blend_max_mb": 60},
        "output": {
            "blend": {
                "format": "blend",
                "max_mb": 100,
                "use_linked_assets": True,
            },
        },
        "output_path": F04_OUTPUT,
    },

    "F05_DIRECTEUR_PHOTO": {
        "input": {"blend_max_mb": 100},
        "output": {
            "blend": {
                "format": "blend",
                "max_mb": 110,
            },
        },
        "output_path": F05_OUTPUT,
    },

    "F06_ALCHIMISTE": {
        "input": {"blend_max_mb": 110},
        "output": {
            "frames": {
                "format": "png",
                "bit_depth": 8,
                "max_mb_per_frame": 6,
                "max_mb_per_chunk_10s": 1500,
            },
        },
        "temp_disk_gb_per_min": 15,
        "output_path": F06_OUTPUT,
    },

    "F07_PORTE_AVIONS": {
        "input": {"frames_format": "png"},
        "output": {
            "video": {
                "codec": "h264",
                "profile": "high",
                "container": "mp4",
                "audio_codec": "aac",
                "audio_bitrate_kbps": 192,
            },
        },
        "output_path": F07_OUTPUT,
    },
}

# ============================================================================
# LIMITES GLOBALES
# ============================================================================

GLOBAL_LIMITS = {
    "chunk_duration_sec": 10,
    "max_chunk_transfer_mb": 150,
    "max_temp_disk_gb": 20,
    "cleanup_after_encode": True,
}

# ============================================================================
# INTERDICTIONS ABSOLUES
# ============================================================================

FORBIDDEN = [
    "depth_lossy_compression",
    "single_file_over_150mb",
    "embedded_textures_in_blend",
    "render_below_540p",
]

# ============================================================================
# FONCTIONS DE VALIDATION
# ============================================================================

def validate_file_size(file_path: str, max_mb: float, context: str = "") -> bool:
    """Valide qu'un fichier ne dépasse pas la limite."""
    import os
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(
            f"[CONTRACT VIOLATION] {context}: {size_mb:.1f} MB > {max_mb} MB limit\n"
            f"File: {file_path}"
        )
    return True


def validate_chunk_size(chunk_dir: str, max_mb: float = 60) -> bool:
    """Valide qu'un chunk ne dépasse pas la limite."""
    import os
    total = sum(
        os.path.getsize(os.path.join(chunk_dir, f))
        for f in os.listdir(chunk_dir)
        if os.path.isfile(os.path.join(chunk_dir, f))
    )
    size_mb = total / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(
            f"[CONTRACT VIOLATION] Chunk too large: {size_mb:.1f} MB > {max_mb} MB\n"
            f"Directory: {chunk_dir}"
        )
    return True


def get_delivery_profile(profile_name: str = "PREMIUM") -> dict:
    """Retourne le profil de livraison demandé."""
    if profile_name not in DELIVERY_PROFILES:
        raise ValueError(f"Unknown profile: {profile_name}. Available: {list(DELIVERY_PROFILES.keys())}")
    return DELIVERY_PROFILES[profile_name]


def get_frigate_contract(frigate_id: str) -> dict:
    """Retourne le contrat d'une frégate."""
    if frigate_id not in FRIGATE_CONTRACTS:
        raise ValueError(f"Unknown frigate: {frigate_id}")
    return FRIGATE_CONTRACTS[frigate_id]


__all__ = [
    'DELIVERY_PROFILES',
    'FRIGATE_CONTRACTS',
    'GLOBAL_LIMITS',
    'FORBIDDEN',
    'validate_file_size',
    'validate_chunk_size',
    'get_delivery_profile',
    'get_frigate_contract',
]
