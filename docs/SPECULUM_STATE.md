# SPECULUM_STATE.md - Phylactère de Résurrection
> État actuel du système EXODUS-SPECULUM

---

## 1. Environnement Technique

### 1.1 Runtime
| Composant | Version | Notes |
|-----------|---------|-------|
| Python | 3.10+ | Google Colab default |
| Blender | 4.0+ | Headless via bpy module |
| CUDA | 11.8+ | Required for GPU inference |
| Platform | Google Colab | T4 GPU, 16GB VRAM |
| OS | Ubuntu 22.04 | Colab runtime |

### 1.2 Dépendances Core

```
# Core ML
torch>=2.0.0+cu118
torchvision>=0.15.0+cu118
torchaudio>=2.0.0+cu118

# Depth Estimation
depth-anything-v2                 # ViT-Large model (335M params)

# Object Detection & Segmentation
ultralytics>=8.0.0               # YOLOv8 detection
segment-anything                  # SAM for precise masks

# AI API
google-generativeai>=0.3.0       # Gemini 1.5 Pro access

# Blender
bpy==4.0.0                       # Blender Python API (headless)

# Image Processing
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0

# Upscaling & Interpolation
realesrgan                       # Real-ESRGAN 4x upscaler
rife-ncnn-vulkan                 # RIFE frame interpolation
# Alternative: flowframes         # GUI wrapper for RIFE

# Video Processing
ffmpeg-python>=0.2.0             # FFmpeg bindings

# Utilities
tqdm>=4.65.0                     # Progress bars
pyyaml>=6.0                      # Config parsing
jsonschema>=4.0.0                # JSON validation
```

### 1.3 APIs & Secrets

```bash
# Variables d'environnement requises
GEMINI_API_KEY=xxx               # Google AI Studio (free tier: 60 QPM)

# Optionnel (futur)
# YOUTUBE_API_KEY=xxx            # Pour automation upload
# TIKTOK_ACCESS_TOKEN=xxx        # Pour automation TikTok
```

**Obtention GEMINI_API_KEY:**
1. Aller sur https://aistudio.google.com/
2. Créer un projet
3. Générer API Key
4. Free tier: 60 requêtes/minute, 1500/jour

---

## 2. Architecture des 8 Frégates (V2-REBIRTH)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXODUS-SPECULUM FLEET V2                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐    ┌──────────┐                                             │
│   │   F00    │    │   F01    │                                             │
│   │  CORTEX  │◄───│ SCANNER  │                                             │
│   │   (AI)   │    │(Extract) │                                             │
│   └────┬─────┘    └────┬─────┘                                             │
│        │               │                                                    │
│        └───────┬───────┘                                                    │
│                ▼                                                            │
│        ┌──────────────┐                                                     │
│        │     F02      │                                                     │
│        │ SCÉNOGRAPHE  │                                                     │
│        │  (Geometry)  │                                                     │
│        └──────┬───────┘                                                     │
│               ▼                                                             │
│        ┌──────────────┐                                                     │
│        │     F03      │                                                     │
│        │PROJECTIONNISTE│                                                    │
│        │  (Mapping)   │                                                     │
│        └──────┬───────┘                                                     │
│               ▼                                                             │
│        ┌──────────────┐                                                     │
│        │     F04      │                                                     │
│        │ LOGISTIQUE   │                                                     │
│        │  (Assets)    │                                                     │
│        └──────┬───────┘                                                     │
│               ▼                                                             │
│        ┌──────────────┐                                                     │
│        │     F05      │                                                     │
│        │DIRECTEUR PHOTO│                                                    │
│        │  (Camera)    │                                                     │
│        └──────┬───────┘                                                     │
│               ▼                                                             │
│        ┌──────────────┐                                                     │
│        │     F06      │                                                     │
│        │ ALCHIMISTE   │                                                     │
│        │  (Render)    │                                                     │
│        └──────┬───────┘                                                     │
│               ▼                                                             │
│        ┌──────────────┐                                                     │
│        │     F07      │                                                     │
│        │PORTE-AVIONS  │                                                     │
│        │  (Output)    │                                                     │
│        └──────────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Description des Frégates (Numérotation V2)

| ID | Nom | Rôle | Input Principal | Output Principal |
|----|-----|------|-----------------|------------------|
| F00 | CORTEX | Intelligence IA | frames + spatial_data | masterplan.json |
| F01 | SCANNER | Extraction données spatiales | video.mp4 | depth_maps/, masks/, spatial_data.json |
| F02 | SCÉNOGRAPHE | Génération géométrie | masterplan + depth | scene_shell.blend |
| F03 | PROJECTIONNISTE | Camera Projection Mapping | scene_shell + frames | scene_projected.blend |
| F04 | LOGISTIQUE | Asset replacement | scene_projected | scene_furnished.blend |
| F05 | DIRECTEUR PHOTO | Camera animation | scene_furnished | scene_animated.blend |
| F06 | ALCHIMISTE | Rendu + Upscaling | scene_animated | frames/ (4K) |
| F07 | PORTE-AVIONS | Assemblage final | frames/ + audio | final_output.mp4 |

### Structure par Frégate (V2-REBIRTH)

```
FRIGATE_XX_NOM/
├── CODEBASE/           # Code Python de la frégate
│   └── __init__.py
├── INPUT/              # Données d'entrée (depuis frégate précédente)
│   └── .gitkeep
└── OUTPUT/             # Résultats générés
    └── .gitkeep
```

---

## 3. Variables Globales de Configuration

```python
# ═══════════════════════════════════════════════════════════════════════════
# TURBO-SPECULUM: Système Tri-Vitesse
# ═══════════════════════════════════════════════════════════════════════════

TURBO_MODE = "conquerant"  # eclaireur | conquerant | souverain

# ═══════════════════════════════════════════════════════════════════════════
# FORMAT-ADAPT: Destination Platform
# ═══════════════════════════════════════════════════════════════════════════

OUTPUT_FORMAT = "HORIZONTAL"  # HORIZONTAL (16:9) | VERTICAL (9:16) | SQUARE (1:1)

# Mapping plateformes
PLATFORM_FORMATS = {
    "youtube": "HORIZONTAL",
    "youtube_shorts": "VERTICAL",
    "tiktok": "VERTICAL",
    "instagram_reels": "VERTICAL",
    "instagram_feed": "SQUARE",
}

# ═══════════════════════════════════════════════════════════════════════════
# RÉSOLUTIONS par Mode x Format
# ═══════════════════════════════════════════════════════════════════════════

RESOLUTION_MATRIX = {
    "eclaireur": {
        "HORIZONTAL": (960, 540),    # 540p
        "VERTICAL": (540, 960),
        "SQUARE": (540, 540)
    },
    "conquerant": {
        "HORIZONTAL": (1920, 1080),  # 1080p
        "VERTICAL": (1080, 1920),
        "SQUARE": (1080, 1080)
    },
    "souverain": {
        "HORIZONTAL": (3840, 2160),  # 4K
        "VERTICAL": (2160, 3840),
        "SQUARE": (2160, 2160)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# RENDER PROFILES par Mode
# ═══════════════════════════════════════════════════════════════════════════

RENDER_PROFILES = {
    "eclaireur": {
        "samples": 16,
        "fps": 12,
        "denoiser": "OPENIMAGEDENOISE",
        "upscale_chain": None
    },
    "conquerant": {
        "samples": 32,
        "fps": 24,
        "denoiser": "OPTIX",
        "upscale_chain": ["ESRGAN_4X", "RIFE_2.5X"]  # 540p→2160p, 24→60fps
    },
    "souverain": {
        "samples": 128,
        "fps": 60,
        "denoiser": "OPTIX",
        "upscale_chain": None  # Native 4K/60
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SMART-CROP Settings
# ═══════════════════════════════════════════════════════════════════════════

SMART_CROP_ENABLED = True
MAX_SENSOR_SHIFT = 0.15        # ±15% du sensor width
MAX_ZOOM_FACTOR = 1.3          # Maximum 30% zoom pour compenser crop
POI_TRACKING_SMOOTHNESS = 0.7  # Lissage mouvement POI (0=instant, 1=statique)

# ═══════════════════════════════════════════════════════════════════════════
# ANTI-PARALLAXE Settings
# ═══════════════════════════════════════════════════════════════════════════

DISPLACEMENT_STRENGTH = 0.5
DISPLACEMENT_MIDLEVEL = 0.5
MULTI_PROJECTION_KEYFRAMES = 3  # Nombre de projections blendées
INPAINT_METHOD = "blender_fill"  # blender_fill | sd_inpaint

# ═══════════════════════════════════════════════════════════════════════════
# HANDHELD CAMERA Settings
# ═══════════════════════════════════════════════════════════════════════════

HANDHELD_Z_FREQ = 1.8          # Hz, fréquence oscillation verticale
HANDHELD_Z_AMPLITUDE = 0.02    # Meters
HANDHELD_ROT_NOISE = 0.005     # Radians, noise rotation XY
HANDHELD_BREATHING_CYCLE = 4.0 # Seconds, cycle respiration

# ═══════════════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════════════

WORKSPACE_ROOT = "/content/exodus_workspace"
ASSETSHUB_PATH = "/content/drive/MyDrive/EXODUS_ASSETS"
OUTPUT_PATH = "/content/output"
TEMP_PATH = "/content/temp"
```

---

## 4. État Actuel du Développement

### 4.1 Checklist Globale

| Composant | Status | Progression |
|-----------|--------|-------------|
| Hexagramme documentaire | ✅ Complet | 100% |
| F00-CORTEX | ⬜ À faire | 0% |
| F01-SCANNER | ✅ Complet | 100% |
| F02-SCÉNOGRAPHE | 🟡 En cours | 80% |
| F03-PROJECTIONNISTE | ✅ Complet | 82% |
| F04-LOGISTIQUE | ⬜ À faire | 0% |
| F05-DIRECTEUR_PHOTO | ⬜ À faire | 0% |
| F06-ALCHIMISTE | ⬜ À faire | 0% |
| F07-PORTE_AVIONS | ⬜ À faire | 0% |
| Tests unitaires | ⬜ À faire | 0% |
| Tests intégration | ⬜ À faire | 0% |

### 4.2 Détail par Frégate

#### F00-CORTEX
- [ ] Gemini API integration
- [ ] Room analysis prompt engineering
- [ ] masterplan.json schema
- [ ] POI heatmap generation

#### F01-SCANNER
- [x] Frame extraction (FFmpeg) ✅ 2026-02-06
- [x] Depth Anything V2 integration ✅ 2026-02-06
- [ ] YOLOv8 object detection
- [ ] SAM segmentation
- [x] spatial_data.json export ✅ 2026-02-06

#### F02-SCÉNOGRAPHE
- [x] Blender headless setup
- [x] Blob geometry generation (6 surfaces)
- [x] Displacement modifier setup
- [x] Proxy cube/cylinder creation
- [x] Ghost proxy tagging
- [x] Collections organization
- [ ] Visual calibration tests

#### F03-PROJECTIONNISTE
- [x] Camera Setup (9 movement types)
- [x] UV Project from Camera (headless compatible)
- [x] Multi-projection shader
- [x] Blend drivers implementation
- [x] Edge feathering
- [ ] Visual calibration tests

#### F04-LOGISTIQUE
- [ ] Ghost Proxy system
- [ ] Asset library structure
- [ ] LOD system
- [ ] Linked asset management

#### F05-DIRECTEUR_PHOTO
- [ ] Sensor shift (Smart-Crop)
- [ ] Handheld F-curves
- [ ] FOV compensation
- [ ] Format conversion matrix

#### F06-ALCHIMISTE
- [ ] Cycles render pipeline
- [ ] OptiX denoiser setup
- [ ] Real-ESRGAN integration
- [ ] RIFE integration

#### F07-PORTE_AVIONS
- [ ] FFmpeg encoding pipeline
- [ ] Audio procedural generation
- [ ] Noise injection anti-fingerprint
- [ ] Multi-format export

---

## 5. Bloqueurs Connus

### 5.1 Bloqueurs Actifs

| ID | Sévérité | Description | Impact | Solution Proposée |
|----|----------|-------------|--------|-------------------|
| BLK-001 | 🟡 Medium | Colab VRAM limite 16GB | Limite taille modèles simultanés | Séquentialiser inférences |
| BLK-002 | 🟡 Medium | Blender bpy installation complexe sur Colab | Setup time | Script d'installation automatisé |

### 5.2 Bloqueurs Résolus

| ID | Description | Solution Appliquée | Date |
|----|-------------|-------------------|------|
| - | - | - | - |

### 5.3 Risques Anticipés

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RSK-001 | Parallaxe visible sur mouvements larges | Haute | Medium | Multi-projection + displacement |
| RSK-002 | Gemini rate limiting | Medium | Low | Caching + retry logic |
| RSK-003 | ESRGAN artefacts sur textures fines | Medium | Medium | Tuning strength, fallback BiCubic |
| RSK-004 | YouTube duplicate detection | Medium | High | Noise injection + variants |

---

## 6. Métriques de Référence

### 6.1 Performance Targets

| Métrique | Éclaireur | Conquérant | Souverain |
|----------|-----------|------------|-----------|
| Render time/frame | <0.5s | <2s | <10s |
| Total pipeline (30s video) | <30min | <2h | <8h |
| VRAM peak | <8GB | <14GB | <16GB |
| Output file size | <50MB | <200MB | <1GB |

### 6.2 Quality Targets

| Métrique | Minimum | Target |
|----------|---------|--------|
| Parallax drift (15° rotation) | <5% | <2% |
| Depth estimation accuracy | >80% | >90% |
| Object detection recall | >70% | >85% |
| Visual quality (SSIM vs source) | >0.85 | >0.92 |

---

*Dernière mise à jour: 2026-02-07*
*Version: 2.0.0-V2-REBIRTH*
