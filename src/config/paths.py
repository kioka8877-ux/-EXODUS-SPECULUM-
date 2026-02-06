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
ROOT_DRIVE = DRIVE_ROOT

# ============================================================================
# SHARED RESOURCES
# ============================================================================

SHARED_RESOURCES = f"{DRIVE_ROOT}/SHARED_RESOURCES/"
AI_MODELS_DIR = f"{SHARED_RESOURCES}AI_MODELS/"
DEPTH_MODEL_BASE_PATH = f"{AI_MODELS_DIR}depth_anything_v2/"
DEPTH_MODEL_PATH = f"{DEPTH_MODEL_BASE_PATH}depth_anything_v2_vitl.pth"

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
    "F03_SCENOGRAPHE": {
        "NAME": "Frégate SCÉNOGRAPHE",
        "DESCRIPTION": "Génération géométrie 3D (blob room + proxies)",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_03_SCENOGRAPHE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_03_SCENOGRAPHE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_03_SCENOGRAPHE/OUTPUT/",
    },
    "F04_PROJECTIONNISTE": {
        "NAME": "Frégate PROJECTIONNISTE",
        "DESCRIPTION": "Camera Projection Mapping pour textures vidéo sur géométrie 3D",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_04_PROJECTIONNISTE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_04_PROJECTIONNISTE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_04_PROJECTIONNISTE/OUTPUT/",
    },
    "F05_LOGISTIQUE": {
        "NAME": "Frégate LOGISTIQUE",
        "DESCRIPTION": "Asset replacement - Ghost Proxy → Real 3D Assets",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_05_LOGISTIQUE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_05_LOGISTIQUE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_05_LOGISTIQUE/OUTPUT/",
    },
    "F06_DIRECTOR": {
        "NAME": "Frégate DIRECTEUR PHOTO",
        "DESCRIPTION": "Camera animation + Smart-Crop",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_06_DIRECTOR/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_06_DIRECTOR/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_06_DIRECTOR/OUTPUT/",
    },
    "F07_ALCHIMISTE": {
        "NAME": "Frégate ALCHIMISTE",
        "DESCRIPTION": "Rendu final + Export vidéo",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_07_ALCHIMISTE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_07_ALCHIMISTE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_07_ALCHIMISTE/OUTPUT/",
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
# RACCOURCIS F03_SCENOGRAPHE
# ============================================================================

F03_CODEBASE = FRIGATES["F03_SCENOGRAPHE"]["CODEBASE"]
F03_INPUT = FRIGATES["F03_SCENOGRAPHE"]["INPUT"]
F03_OUTPUT = FRIGATES["F03_SCENOGRAPHE"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F04_PROJECTIONNISTE
# ============================================================================

F04_CODEBASE = FRIGATES["F04_PROJECTIONNISTE"]["CODEBASE"]
F04_INPUT = FRIGATES["F04_PROJECTIONNISTE"]["INPUT"]
F04_OUTPUT = FRIGATES["F04_PROJECTIONNISTE"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F05_LOGISTIQUE
# ============================================================================

F05_CODEBASE = FRIGATES["F05_LOGISTIQUE"]["CODEBASE"]
F05_INPUT = FRIGATES["F05_LOGISTIQUE"]["INPUT"]
F05_OUTPUT = FRIGATES["F05_LOGISTIQUE"]["OUTPUT"]

# ============================================================================
# ASSETSHUB - Bibliothèque d'assets 3D
# ============================================================================

ASSETSHUB_PATH = f"{DRIVE_ROOT}/ASSETSHUB/"

# ============================================================================
# RACCOURCIS F06_DIRECTOR
# ============================================================================

F06_CODEBASE = FRIGATES["F06_DIRECTOR"]["CODEBASE"]
F06_INPUT = FRIGATES["F06_DIRECTOR"]["INPUT"]
F06_OUTPUT = FRIGATES["F06_DIRECTOR"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F07_ALCHIMISTE
# ============================================================================

F07_CODEBASE = FRIGATES["F07_ALCHIMISTE"]["CODEBASE"]
F07_INPUT = FRIGATES["F07_ALCHIMISTE"]["INPUT"]
F07_OUTPUT = FRIGATES["F07_ALCHIMISTE"]["OUTPUT"]

# ============================================================================
# EXPORTS
# ============================================================================

# ============================================================================
# PATHCONFIG - Classe unifiée pour accès aux chemins
# ============================================================================

class PathConfig:
    """Classe de configuration des chemins pour accès unifié."""
    DRIVE_ROOT = DRIVE_ROOT
    
    MASTERPLAN_PATH = f"{F00_OUTPUT}masterplan.json"
    DEPTH_OUTPUT = f"{F01_OUTPUT}depth_maps/"
    FRAMES_OUTPUT = f"{F01_OUTPUT}frames/"
    
    SCENOGRAPHE_OUTPUT = F03_OUTPUT
    SCENE_SHELL_PATH = f"{F03_OUTPUT}scene_shell.blend"
    
    PROJECTIONNISTE_OUTPUT = F04_OUTPUT
    SCENE_PROJECTED_PATH = f"{F04_OUTPUT}scene_projected.blend"
    
    LOGISTIQUE_OUTPUT = F05_OUTPUT
    SCENE_FURNISHED_PATH = f"{F05_OUTPUT}scene_furnished.blend"
    ASSETSHUB_PATH = ASSETSHUB_PATH


__all__ = [
    'DRIVE_ROOT',
    'ROOT_DRIVE',
    'SHARED_RESOURCES',
    'AI_MODELS_DIR',
    'DEPTH_MODEL_BASE_PATH',
    'DEPTH_MODEL_PATH',
    'FRIGATES',
    'F00_CODEBASE', 'F00_INPUT', 'F00_OUTPUT',
    'F01_CODEBASE', 'F01_INPUT', 'F01_OUTPUT',
    'F02_CODEBASE', 'F02_INPUT', 'F02_OUTPUT',
    'F03_CODEBASE', 'F03_INPUT', 'F03_OUTPUT',
    'F04_CODEBASE', 'F04_INPUT', 'F04_OUTPUT',
    'F05_CODEBASE', 'F05_INPUT', 'F05_OUTPUT',
    'F06_CODEBASE', 'F06_INPUT', 'F06_OUTPUT',
    'F07_CODEBASE', 'F07_INPUT', 'F07_OUTPUT',
    'ASSETSHUB_PATH',
    'PathConfig',
]
