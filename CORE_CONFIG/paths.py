#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Configuration des Chemins Sacrés
Constantes Divines pour Google Colab + Drive.

PROTOCOLE GITHUB-FORGE:
- Ces chemins sont des CONSTANTES - ne pas vérifier leur existence
- Le code doit fonctionner sur Colab vierge après clone + mount
- Pas de os.path.exists() - utiliser les paths directement

MIGRATION V2-REBIRTH (2026-02-07):
- Renumération: F03-F08 → F02-F07 (suppression gap F02_ARCHITECT)
- Structure: FRIGATE_XX_NOM/{CODEBASE,INPUT,OUTPUT}
- 8 Frégates actives: F00-F07
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

YOLO_MODEL_PATH = f"{AI_MODELS_DIR}yolov8/yolov8x.pt"

SAM_MODEL_PATH = f"{AI_MODELS_DIR}sam/sam_vit_h_4b8939.pth"
SAM_MODEL_TYPE = "vit_h"

# ============================================================================
# CONFIGURATION FRÉGATES (V2-REBIRTH: F00-F07)
# ============================================================================

FRIGATES = {
    "F00_CORTEX": {
        "NAME": "Frégate CORTEX",
        "DESCRIPTION": "Intelligence IA - Analyse Gemini 1.5 Pro",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_00_CORTEX/OUTPUT/",
    },
    "F01_SCANNER": {
        "NAME": "Frégate SCANNER",
        "DESCRIPTION": "Extraction vidéo et depth estimation",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_01_SCANNER/OUTPUT/",
    },
    "F02_SCENOGRAPHE": {
        "NAME": "Frégate SCÉNOGRAPHE",
        "DESCRIPTION": "Génération géométrie 3D (blob room + proxies)",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_02_SCENOGRAPHE/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_02_SCENOGRAPHE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_02_SCENOGRAPHE/OUTPUT/",
    },
    "F03_PROJECTIONNISTE": {
        "NAME": "Frégate PROJECTIONNISTE",
        "DESCRIPTION": "Camera Projection Mapping pour textures vidéo sur géométrie 3D",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_03_PROJECTIONNISTE/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_03_PROJECTIONNISTE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_03_PROJECTIONNISTE/OUTPUT/",
    },
    "F04_LOGISTIQUE": {
        "NAME": "Frégate LOGISTIQUE",
        "DESCRIPTION": "Asset replacement - Ghost Proxy → Real 3D Assets",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_04_LOGISTIQUE/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_04_LOGISTIQUE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_04_LOGISTIQUE/OUTPUT/",
    },
    "F05_DIRECTEUR_PHOTO": {
        "NAME": "Frégate DIRECTEUR PHOTO",
        "DESCRIPTION": "Camera animation + Smart-Crop",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_05_DIRECTEUR_PHOTO/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_05_DIRECTEUR_PHOTO/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_05_DIRECTEUR_PHOTO/OUTPUT/",
    },
    "F06_ALCHIMISTE": {
        "NAME": "Frégate ALCHIMISTE",
        "DESCRIPTION": "Rendu Cycles + Upscaling IA (ESRGAN/RIFE)",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_06_ALCHIMISTE/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_06_ALCHIMISTE/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_06_ALCHIMISTE/OUTPUT/",
    },
    "F07_PORTE_AVIONS": {
        "NAME": "Frégate PORTE-AVIONS",
        "DESCRIPTION": "Assemblage final - Encodage + Audio ASMR + Export multi-plateformes",
        "CODEBASE": f"{DRIVE_ROOT}/FRIGATE_07_PORTE_AVIONS/CODEBASE/",
        "INPUT": f"{DRIVE_ROOT}/FRIGATE_07_PORTE_AVIONS/INPUT/",
        "OUTPUT": f"{DRIVE_ROOT}/FRIGATE_07_PORTE_AVIONS/OUTPUT/",
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
# RACCOURCIS F02_SCENOGRAPHE
# ============================================================================

F02_CODEBASE = FRIGATES["F02_SCENOGRAPHE"]["CODEBASE"]
F02_INPUT = FRIGATES["F02_SCENOGRAPHE"]["INPUT"]
F02_OUTPUT = FRIGATES["F02_SCENOGRAPHE"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F03_PROJECTIONNISTE
# ============================================================================

F03_CODEBASE = FRIGATES["F03_PROJECTIONNISTE"]["CODEBASE"]
F03_INPUT = FRIGATES["F03_PROJECTIONNISTE"]["INPUT"]
F03_OUTPUT = FRIGATES["F03_PROJECTIONNISTE"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F04_LOGISTIQUE
# ============================================================================

F04_CODEBASE = FRIGATES["F04_LOGISTIQUE"]["CODEBASE"]
F04_INPUT = FRIGATES["F04_LOGISTIQUE"]["INPUT"]
F04_OUTPUT = FRIGATES["F04_LOGISTIQUE"]["OUTPUT"]

# ============================================================================
# ASSETSHUB - Bibliothèque d'assets 3D
# ============================================================================

ASSETSHUB_PATH = f"{DRIVE_ROOT}/ASSETSHUB/"

# ============================================================================
# RACCOURCIS F05_DIRECTEUR_PHOTO
# ============================================================================

F05_CODEBASE = FRIGATES["F05_DIRECTEUR_PHOTO"]["CODEBASE"]
F05_INPUT = FRIGATES["F05_DIRECTEUR_PHOTO"]["INPUT"]
F05_OUTPUT = FRIGATES["F05_DIRECTEUR_PHOTO"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F06_ALCHIMISTE
# ============================================================================

F06_CODEBASE = FRIGATES["F06_ALCHIMISTE"]["CODEBASE"]
F06_INPUT = FRIGATES["F06_ALCHIMISTE"]["INPUT"]
F06_OUTPUT = FRIGATES["F06_ALCHIMISTE"]["OUTPUT"]

# ============================================================================
# RACCOURCIS F07_PORTE_AVIONS
# ============================================================================

F07_CODEBASE = FRIGATES["F07_PORTE_AVIONS"]["CODEBASE"]
F07_INPUT = FRIGATES["F07_PORTE_AVIONS"]["INPUT"]
F07_OUTPUT = FRIGATES["F07_PORTE_AVIONS"]["OUTPUT"]

# ============================================================================
# PATHCONFIG - Classe unifiée pour accès aux chemins
# ============================================================================

class PathConfig:
    """Classe de configuration des chemins pour accès unifié."""
    DRIVE_ROOT = DRIVE_ROOT
    
    MASTERPLAN_PATH = f"{F00_OUTPUT}masterplan.json"
    DEPTH_OUTPUT = f"{F01_OUTPUT}depth_maps/"
    FRAMES_OUTPUT = f"{F01_OUTPUT}frames/"
    
    SCENOGRAPHE_OUTPUT = F02_OUTPUT
    SCENE_SHELL_PATH = f"{F02_OUTPUT}scene_shell.blend"
    
    PROJECTIONNISTE_OUTPUT = F03_OUTPUT
    SCENE_PROJECTED_PATH = f"{F03_OUTPUT}scene_projected.blend"
    
    LOGISTIQUE_OUTPUT = F04_OUTPUT
    SCENE_FURNISHED_PATH = f"{F04_OUTPUT}scene_furnished.blend"
    ASSETSHUB_PATH = ASSETSHUB_PATH
    
    DIRECTEUR_PHOTO_OUTPUT = F05_OUTPUT
    SCENE_ANIMATED_PATH = f"{F05_OUTPUT}scene_animated.blend"
    
    ALCHIMISTE_OUTPUT = F06_OUTPUT
    TEMP_RENDER_PATH = f"{F06_OUTPUT}temp_render.mp4"
    
    PORTE_AVIONS_OUTPUT = FRIGATES["F07_PORTE_AVIONS"]["OUTPUT"]
    FINAL_OUTPUT_PATH = f"{FRIGATES['F07_PORTE_AVIONS']['OUTPUT']}FINAL_SPECULUM_TOUR_4K.mp4"


__all__ = [
    'DRIVE_ROOT',
    'ROOT_DRIVE',
    'SHARED_RESOURCES',
    'AI_MODELS_DIR',
    'DEPTH_MODEL_BASE_PATH',
    'DEPTH_MODEL_PATH',
    'YOLO_MODEL_PATH',
    'SAM_MODEL_PATH',
    'SAM_MODEL_TYPE',
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
