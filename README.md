# 🌌 EXODUS-SPECULUM

> Transforme des vidéos immobilières réelles en clones 3D 4K/60FPS ultra-réalistes via Camera Projection Mapping.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Blender](https://img.shields.io/badge/Blender-4.0+-orange.svg)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Google%20Colab-yellow.svg)](https://colab.research.google.com/)

---

## 🎯 Mission

**EXODUS-SPECULUM** est un pipeline de production industrielle qui transforme une seule vidéo immobilière en multiples variantes 3D haute qualité pour YouTube, TikTok et Instagram.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Vidéo Source   │────►│  EXODUS-SPECULUM │────►│  N Variantes    │
│  (1080p/30fps)  │     │  Pipeline IA     │     │  (4K/60fps)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Caractéristiques Clés

- 🆓 **100% Gratuit** - Utilise uniquement des outils open source et APIs free tier
- 🚀 **Production Industrielle** - Génère des variantes multiples anti-shadowban
- 🎬 **Multi-Format** - Export automatique YouTube, TikTok, Instagram
- 🧠 **IA Avancée** - Depth estimation, segmentation, analyse Gemini
- 💻 **Cloud Ready** - Conçu pour Google Colab (T4 GPU, 16GB VRAM)

---

## 🏗️ Architecture (V2-REBIRTH)

Le pipeline est organisé en **8 Frégates** (modules spécialisés) avec structure autonome:

```
     Video Input
          │
          ▼
    ┌───────────┐     ┌───────────┐
    │    F00    │     │    F01    │
    │  CORTEX   │◄────│  SCANNER  │
    │   (AI)    │     │ (Extract) │
    └─────┬─────┘     └─────┬─────┘
          │                 │
          └────────┬────────┘
                   ▼
           ┌─────────────┐
           │     F02     │
           │ SCÉNOGRAPHE │
           │ (Geometry)  │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │     F03     │
           │PROJECTIONNISTE│
           │  (Mapping)  │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │     F04     │
           │ LOGISTIQUE  │
           │  (Assets)   │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │     F05     │
           │DIRECTEUR PHOTO│
           │  (Camera)   │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │     F06     │
           │ ALCHIMISTE  │
           │  (Render)   │
           └──────┬──────┘
                  ▼
           ┌─────────────┐
           │     F07     │
           │PORTE-AVIONS │
           │  (Output)   │
           └─────────────┘
                  │
                  ▼
          Video Output(s)
```

| Frégate | Rôle | Technologies |
|---------|------|--------------|
| F00 CORTEX | Intelligence IA | Gemini 1.5 Pro |
| F01 SCANNER | Extraction données spatiales | FFmpeg, Depth Anything V2, YOLOv8, SAM |
| F02 SCÉNOGRAPHE | Génération géométrie 3D | Blender bpy |
| F03 PROJECTIONNISTE | Camera Projection Mapping | Blender UV Project |
| F04 LOGISTIQUE | Asset replacement | Blender Linked Libraries |
| F05 DIRECTEUR PHOTO | Animation caméra | Blender F-curves |
| F06 ALCHIMISTE | Rendu + Upscaling | Cycles, Real-ESRGAN, RIFE |
| F07 PORTE-AVIONS | Assemblage final | FFmpeg, Audio procedural |

---

## ⚡ Modes de Qualité (TURBO-SPECULUM)

| Mode | Résolution | FPS | Temps (30sec) | Usage |
|------|------------|-----|---------------|-------|
| 🔍 **ÉCLAIREUR** | 540p | 12 | <30min | Preview, tests |
| ⚔️ **CONQUÉRANT** | 4K (upscaled) | 60 | <2h | Production standard |
| 👑 **SOUVERAIN** | 4K (native) | 60 | <8h | Showcase, premium |

---

## 🛠️ Stack Technologique

### Core
- **Python 3.10+** - Runtime principal
- **Blender 4.0+** - Engine 3D (headless via bpy)
- **Google Colab** - Plateforme compute (T4 GPU)

### IA & ML
- **Depth Anything V2** - Estimation de profondeur (ViT-Large)
- **YOLOv8** - Détection d'objets
- **SAM** - Segmentation précise
- **Gemini 1.5 Pro** - Analyse vision (free tier)

### Post-Processing
- **Real-ESRGAN** - Upscaling 4x
- **RIFE** - Interpolation 2.5x
- **FFmpeg** - Encoding vidéo

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📜 SPECULUM_STATE.md](docs/SPECULUM_STATE.md) | État technique du système |
| [📋 SPECULUM_PRD.md](docs/SPECULUM_PRD.md) | Spécifications fonctionnelles |
| [🗺️ SPECULUM_ROADMAP.md](docs/SPECULUM_ROADMAP.md) | Plan de développement |
| [📝 SPECULUM_LOGBOOK.md](docs/SPECULUM_LOGBOOK.md) | Registre des tâches |
| [📓 SPECULUM_DEVLOG.md](docs/SPECULUM_DEVLOG.md) | Journal technique |
| [✅ SPECULUM_VALIDATION.md](docs/SPECULUM_VALIDATION.md) | Protocoles de test |

---

## 🚀 Quick Start

### Prérequis
- Compte Google (pour Colab)
- API Key Gemini (gratuit sur [AI Studio](https://aistudio.google.com/))

### Installation

```bash
# Clone le repository
git clone https://github.com/kioka8877-ux/-EXODUS-SPECULUM-.git
cd -EXODUS-SPECULUM-

# Ouvre le notebook Colab (à venir)
# Ou exécute localement avec GPU NVIDIA
```

### Usage Basique

```python
# À venir après implémentation
from CORE_CONFIG.paths import PathConfig
from FRIGATE_01_SCANNER.CODEBASE import ScannerPipeline

pipeline = ScannerPipeline()
pipeline.process("video_source.mp4")
```

---

## 📊 Roadmap

- [x] **Phase 0** - Documentation (Hexagramme)
- [ ] **Phase 1** - Proof of Concept (Semaine 2-3)
- [ ] **Phase 2** - Core Pipeline (Semaine 4-6)
- [ ] **Phase 3** - Industrialisation (Semaine 7-8)

Voir [SPECULUM_ROADMAP.md](docs/SPECULUM_ROADMAP.md) pour les détails.

---

## 🔑 Concepts Clés

### Camera Projection Mapping
Technique qui projette une image 2D sur une géométrie 3D depuis le point de vue de la caméra, créant l'illusion de profondeur lors du mouvement.

### Multi-Projection Blending
Utilise 3 keyframes (début, milieu, fin) avec transition douce pour minimiser les artefacts de parallaxe.

### Smart-Crop (Sensor Shift)
Recadrage intelligent qui utilise le sensor shift de Blender plutôt qu'un crop destructif, préservant la perspective.

### Anti-Shadowban
Système de variantes qui modifie imperceptiblement chaque export (couleur, bruit, audio) pour éviter la détection de duplicates.

---

## 📁 Structure du Projet (V2-REBIRTH)

```
EXODUS-SPECULUM/
├── FRIGATE_00_CORTEX/          # Intelligence IA
│   ├── CODEBASE/               # Code Python
│   ├── INPUT/                  # Entrées
│   └── OUTPUT/                 # Sorties
├── FRIGATE_01_SCANNER/         # Extraction données spatiales
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_02_SCENOGRAPHE/     # Génération géométrie 3D
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_03_PROJECTIONNISTE/ # Camera Projection Mapping
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_04_LOGISTIQUE/      # Asset replacement
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_05_DIRECTEUR_PHOTO/ # Animation caméra
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_06_ALCHIMISTE/      # Rendu + Upscaling
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── FRIGATE_07_PORTE_AVIONS/    # Assemblage final
│   ├── CODEBASE/
│   ├── INPUT/
│   └── OUTPUT/
├── CORE_CONFIG/                # Configuration centrale
│   └── paths.py
├── CORE_TOOLS/                 # Scripts utilitaires
│   ├── install_dependencies.py
│   └── test_shared_resources.py
├── docs/                       # Documentation (Hexagramme)
│   ├── SPECULUM_STATE.md
│   ├── SPECULUM_PRD.md
│   ├── SPECULUM_ROADMAP.md
│   ├── SPECULUM_LOGBOOK.md
│   ├── SPECULUM_DEVLOG.md
│   └── SPECULUM_VALIDATION.md
├── notebooks/                  # Notebooks Colab
└── README.md
```

---

## 🤝 Contribution

Les contributions sont bienvenues ! Voir le [SPECULUM_LOGBOOK.md](docs/SPECULUM_LOGBOOK.md) pour les tâches disponibles.

1. Fork le projet
2. Crée une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

---

## 📜 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Depth Anything](https://github.com/DepthAnything/Depth-Anything-V2) - Estimation de profondeur
- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8
- [Segment Anything](https://github.com/facebookresearch/segment-anything) - SAM
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - Upscaling
- [RIFE](https://github.com/nihui/rife-ncnn-vulkan) - Frame interpolation
- [Blender](https://www.blender.org/) - Engine 3D

---

<p align="center">
  <b>EXODUS-SPECULUM</b> - Forgé dans les Annales de la Création
</p>
