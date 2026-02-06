#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Configuration des Chemins Sacrés
Constantes Divines pour Google Colab + Drive.

PROTOCOLE GITHUB-FORGE:
- Ces chemins sont des CONSTANTES - ne pas vérifier leur existence
- Le code doit fonctionner sur Colab vierge après clone + mount
- Pas de os.path.exists() - utiliser les paths directement
"""

# ============================================================================
# RACINE DRIVE
# ============================================================================

DRIVE_ROOT = "/content/drive/MyDrive/EXODUS-SPECULUM"

# ============================================================================
# CONFIGURATION FRÉGATES
# ============================================================================

FRIGATES = {
    "F00_CORTEX": {
        "NAME": "Frégate CORTEX",
        "DESCRIPTION": "Intelligence IA - Analyse Gemini 1.5 Pro",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/OUTPUT/",
    },
    "F01_SCANNER": {
        "NAME": "Frégate SCANNER",
        "DESCRIPTION": "Extraction vidéo et depth estimation",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/OUTPUT/",
    },
    "F02_ARCHITECT": {
        "NAME": "Frégate ARCHITECT",
        "DESCRIPTION": "Reconstruction 3D Blender",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_02_ARCHITECT/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_02_ARCHITECT/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_02_ARCHITECT/OUTPUT/",
    },
    "F03_RENDERER": {
        "NAME": "Frégate RENDERER",
        "DESCRIPTION": "Rendu Cycles + Post-processing",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_03_RENDERER/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_03_RENDERER/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_03_RENDERER/OUTPUT/",
    },
    "F04_COMPOSITOR": {
        "NAME": "Frégate COMPOSITOR",
        "DESCRIPTION": "Upscaling + Interpolation + Export final",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_04_COMPOSITOR/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_04_COMPOSITOR/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_04_COMPOSITOR/OUTPUT/",
    },
}

# ============================================================================
# RACCOURCIS F00_CORTEX
# ============================================================================

F00_CODEBASE = FRIGATES["F00_CORTEX"]["CODEBASE"]
F00_INPUT = FRIGATES["F00_CORTEX"]["INPUT"]
F00_OUTPUT = FRIGATES["F00_CORTEX"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F01_SCANNER
# ============================================================================

F01_CODEBASE = FRIGATES["F01_SCANNER"]["CODEBASE"]
F01_INPUT = FRIGATES["F01_SCANNER"]["INPUT"]
F01_OUTPUT = FRIGATES["F01_SCANNER"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F02_ARCHITECT
# ============================================================================

F02_CODEBASE = FRIGATES["F02_ARCHITECT"]["CODEBASE"]
F02_INPUT = FRIGATES["F02_ARCHITECT"]["INPUT"]
F02_OUTPUT = FRIGATES["F02_ARCHITECT"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F03_RENDERER
# ============================================================================

F03_CODEBASE = FRIGATES["F03_RENDERER"]["CODEBASE"]
F03_INPUT = FRIGATES["F03_RENDERER"]["INPUT"]
F03_OUTPUT = FRIGATES["F03_RENDERER"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F04_COMPOSITOR
# ============================================================================

F04_CODEBASE = FRIGATES["F04_COMPOSITOR"]["CODEBASE"]
F04_INPUT = FRIGATES["F04_COMPOSITOR"]["INPUT"]
F04_OUTPUT = FRIGATES["F04_COMPOSITOR"]["OUTPUT"]

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DRIVE_ROOT',
    'FRIGATES',
    'F00_CODEBASE', 'F00_INPUT', 'F00_OUTPUT',
    'F01_CODEBASE', 'F01_INPUT', 'F01_OUTPUT',
    'F02_CODEBASE', 'F02_INPUT', 'F02_OUTPUT',
    'F03_CODEBASE', 'F03_INPUT', 'F03_OUTPUT',
    'F04_CODEBASE', 'F04_INPUT', 'F04_OUTPUT',
]
