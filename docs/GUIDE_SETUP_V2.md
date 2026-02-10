# 🔧 GUIDE - Setup DRIVE_EXODUS_V2

> **EXODUS-SPECULUM V2 - Configuration de l'arborescence Drive**
>
> Ce guide vous accompagne dans la création de la structure complète sur Google Drive. Opération à faire **une seule fois**.


## 📋 Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Prérequis](#2-prérequis)
3. [Instructions pas à pas](#3-instructions-pas-à-pas)
4. [Flux de données entre unités](#4-flux-de-données-entre-unités)
5. [Contenu à placer manuellement](#5-contenu-à-placer-manuellement)
6. [Troubleshooting](#6-troubleshooting)
7. [Liens rapides](#7-liens-rapides)


## 1. Vue d'ensemble

### Architecture des Unités (00-06)

| Unité | Nom | Rôle |
|-------|-----|------|
| **00** | CORTEX_HQ | 🧠 Intelligence IA - Analyse vidéo source → génère `PRODUCTION_PLAN.JSON` |
| **01** | ANIMATION_ENGINE | 🎭 Fusion MoCap Mixamo avec animations personnalisées → `.abc/.blend` |
| **02** | LOGISTICS_DEPOT | 📦 Équipement avatars Roblox + bibliothèque props → acteurs bakés |
| **03** | SCENOGRAPHY_DOCK | 🏔️ Conversion cartes Minecraft + HDRi → scènes environnement |
| **04** | PHOTOGRAPHY_WING | 📷 Configuration caméra et tracking vidéo → logique caméra |
| **05** | ALCHEMIST_LAB | 🧪 Color grading, LUTs et compositing → frames finales |
| **06** | AIRCRAFT_CARRIER | 🚀 Assemblage final → vidéo 4K/120FPS |

### EXODUS_AI_MODELS (Ressources partagées)

| Dossier | Contenu |
|---------|---------|
| `BLENDER/` | Blender 4.0 portable |
| `EMOCA/` | Modèle extraction faciale |
| `RIFE/` | Modèle interpolation frames |
| `REALESRGAN/` | Modèle upscale |
| `McPrep/` | Addon Minecraft pour Blender |
| `HDRi/` | Collection HDRi partagée |


## 2. Prérequis

| ✅ Requis | Description |
|-----------|-------------|
| Compte Google | Nécessaire pour Colab et Drive |
| ~10GB espace Drive | Pour la structure + modèles IA |
| Connexion stable | Pour les futurs téléchargements |
| ~1 minute | Temps création structure |


## 3. Instructions pas à pas

### Étape 1: Ouvrir le notebook

Cliquez sur ce lien pour ouvrir le notebook de setup:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SETUP_DRIVE_V2.ipynb)

### Étape 2: Autoriser l'accès Drive

1. Exécutez la **Cellule 2** (Montage Drive)
2. Une fenêtre popup apparaît → **Cliquez "Se connecter à Google Drive"**
3. Choisissez votre compte Google
4. Autorisez l'accès

> ⚠️ **Important**: Sans cette autorisation, la structure ne sera pas créée sur Drive!

### Étape 3: Exécuter les cellules

Exécutez chaque cellule **dans l'ordre**:

| Cellule | Contenu | Durée |
|---------|---------|-------|
| 1 | Header (info) | - |
| 2 | Montage Drive | ~10 sec |
| 3 | Création structure | ~15 sec |
| 4 | Vérification visuelle | ~5 sec |
| 5 | Création READMEs | ~5 sec |
| 6 | Rapport final | ~2 sec |

### Étape 4: Vérifier le rapport

La cellule finale affiche un rapport:

```
============================================================
📊 RAPPORT SETUP DRIVE_EXODUS_V2
============================================================
📁 Racine: /content/drive/MyDrive/DRIVE_EXODUS_V2
📂 Unités: 7 + EXODUS_AI_MODELS
📄 READMEs: 8 fichiers
============================================================

🚀 STRUCTURE PRÊTE!

📖 Prochaine étape: Télécharger les modèles IA dans EXODUS_AI_MODELS/
```


## 4. Flux de données entre unités

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUX DE DONNÉES EXODUS V2                            │
└─────────────────────────────────────────────────────────────────────────────┘

📹 VIDÉO SOURCE
      │
      ▼
┌─────────────────────┐
│   00_CORTEX_HQ      │
│   IN_VIDEO_SOURCE   │──────────────────────────────────────────┐
│   OUT → PRODUCTION_ │                                          │
│         PLAN.JSON   │                                          │
└─────────┬───────────┘                                          │
          │                                                      │
          │ PRODUCTION_PLAN.JSON                                 │
          ▼                                                      │
┌─────────────────────┐                                          │
│ 01_ANIMATION_ENGINE │                                          │
│ IN_CORTEX_JSON ◄────┤                                          │
│ IN_MIXAMO_BASE ◄────┤ body_motion.fbx (MoCap)                  │
│ OUT → MOTION_DATA   │ (.abc/.blend)                            │
└─────────┬───────────┘                                          │
          │                                                      │
          │ Animation fusionnée                                  │
          ▼                                                      │
┌─────────────────────┐                                          │
│ 02_LOGISTICS_DEPOT  │                                          │
│ IN_MOTION_DATA ◄────┤                                          │
│ IN_ROBLOX_AVATAR ◄──┤ Avatar .blend                            │
│ IN_PROPS_LIBRARY ◄──┤ Bibliothèque props                       │
│ OUT → BAKED_ACTORS  │ (.abc)                                   │
└─────────┬───────────┘                                          │
          │                                                      │
          │ Acteurs équipés                                      │
          │                                                      │
          │              ┌─────────────────────┐                 │
          │              │ 03_SCENOGRAPHY_DOCK │                 │
          │              │ IN_MAP_RAW ◄────────┤ Carte Minecraft │
          │              │   ├─ hdri_library/  │ + HDRi          │
          │              │   └─ environment_   │                 │
          │              │      assets/        │                 │
          │              │ IN_CORTEX_JSON ◄────┼─────────────────┘
          │              │ OUT → PREMIUM_SCENE │ (.blend)         
          │              └─────────┬───────────┘                  
          │                        │                              
          │    ┌───────────────────┘                              
          │    │ Scènes environnement                             
          ▼    ▼                                                  
┌─────────────────────┐                                          
│ 04_PHOTOGRAPHY_WING │                                          
│ IN_VIDEO_SOURCE ◄───┼─────────────────────── 📹 Vidéo référence
│ IN_SCENE_REF ◄──────┤ (.blend de U03)                          
│ OUT → CAMERA_LOGIC  │ (scènes + caméra)                        
└─────────┬───────────┘                                          
          │                                                      
          │ Scènes avec caméra                                   
          │                                                      
    ┌─────┴─────┐                                                
    │  RENDU    │ (EXR séquences)                                
    └─────┬─────┘                                                
          │                                                      
          ▼                                                      
┌─────────────────────┐                                          
│   05_ALCHEMIST_LAB  │                                          
│ IN_RAW_FRAMES ◄─────┤ Séquences EXR                            
│ LUTS/ ◄─────────────┤ Fichiers .cube                           
│ OUT → FINAL_FRAMES  │ (frames gradées)                         
└─────────┬───────────┘                                          
          │                                                      
          │ Frames finales                                       
          ▼                                                      
┌─────────────────────┐                                          
│ 06_AIRCRAFT_CARRIER │                                          
│ IN_ASSEMBLY_KIT ◄───┤ Frames + Audio                           
│ OUT → FINAL_MOVIE   │ 🎬 4K/120FPS                              
└─────────────────────┘                                          


┌─────────────────────┐
│   EXODUS_AI_MODELS  │  ← Ressources partagées par toutes unités
│   BLENDER/          │
│   EMOCA/            │
│   RIFE/             │
│   REALESRGAN/       │
│   McPrep/           │
│   HDRi/             │
└─────────────────────┘
```


## 5. Contenu à placer manuellement

Après création de la structure, vous devez ajouter vos fichiers:

### Fichiers source (obligatoires)

| Dossier | Fichiers à ajouter | Format |
|---------|-------------------|--------|
| `00_CORTEX_HQ/IN_VIDEO_SOURCE/` | Vidéo source à analyser | `.mp4`, `.mov` |
| `01_ANIMATION_ENGINE/IN_MIXAMO_BASE/` | MoCap body motion | `.fbx` |
| `02_LOGISTICS_DEPOT/IN_ROBLOX_AVATAR/` | Avatar Roblox | `.blend` |
| `03_SCENOGRAPHY_DOCK/IN_MAP_RAW/` | Carte Minecraft exportée | `.obj`, `.blend` |

### Bibliothèques (optionnels mais recommandés)

| Dossier | Fichiers à ajouter | Format |
|---------|-------------------|--------|
| `02_LOGISTICS_DEPOT/IN_PROPS_LIBRARY/` | Props 3D (armes, objets) | `.blend`, `.fbx` |
| `03_SCENOGRAPHY_DOCK/IN_MAP_RAW/hdri_library/` | Fichiers HDRi | `.hdr`, `.exr` |
| `03_SCENOGRAPHY_DOCK/IN_MAP_RAW/environment_assets/` | Assets environnement | `.blend` |
| `05_ALCHEMIST_LAB/LUTS/` | Fichiers LUT color grading | `.cube` |

### Modèles IA (téléchargement séparé)

| Dossier | Contenu | Source |
|---------|---------|--------|
| `EXODUS_AI_MODELS/BLENDER/` | Blender 4.0 portable | [blender.org](https://www.blender.org/download/) |
| `EXODUS_AI_MODELS/EMOCA/` | Modèle extraction faciale | [GitHub EMOCA](https://github.com/radekd91/emoca) |
| `EXODUS_AI_MODELS/RIFE/` | Modèle interpolation | [GitHub RIFE](https://github.com/megvii-research/ECCV2022-RIFE) |
| `EXODUS_AI_MODELS/REALESRGAN/` | Modèle upscale | [GitHub Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) |
| `EXODUS_AI_MODELS/McPrep/` | Addon Minecraft Blender | [GitHub McPrep](https://github.com/Moo-Ack-Productions/MCprep) |
| `EXODUS_AI_MODELS/HDRi/` | Collection HDRi | [Poly Haven](https://polyhaven.com/hdris) |


## 6. Troubleshooting

### ❌ Erreur quota Drive

**Symptôme:** `Quota exceeded` ou `Not enough space`

**Solution:**
1. Vérifiez votre espace Drive: [drive.google.com/settings/storage](https://drive.google.com/settings/storage)
2. Libérez au moins 10GB
3. Videz la corbeille Drive (les fichiers supprimés comptent!)
4. Réexécutez le notebook


### ❌ Drive non monté

**Symptôme:** `FileNotFoundError: /content/drive/MyDrive/...`

**Solution:**
1. Réexécutez la Cellule 2 (Montage Drive)
2. Acceptez les permissions dans le popup
3. Continuez avec les autres cellules


### ❌ Dossier déjà existant

**Symptôme:** Warning "Directory already exists"

**Solution:** C'est normal! `os.makedirs(exist_ok=True)` ignore les dossiers existants.


### ❌ Timeout Colab

**Symptôme:** Session déconnectée

**Solution:**
1. Reconnectez-vous à Colab
2. Réexécutez la Cellule 2 (Montage Drive)
3. Les dossiers existants seront conservés
4. Continuez avec les cellules restantes


### ❌ Arborescence incomplète

**Symptôme:** Certains dossiers manquent

**Solution:**
1. Exécutez la Cellule 4 (Vérification visuelle)
2. Identifiez les dossiers manquants
3. Réexécutez la Cellule 3 (Création structure)


## 7. Liens rapides

### 📂 Notebooks

| Notebook | Description | Lien |
|----------|-------------|------|
| SETUP_DRIVE_V2.ipynb | Création structure (ce setup) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SETUP_DRIVE_V2.ipynb) |
| SPECULUM_COLAB_TEMPLATE.ipynb | Pipeline complet | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb) |

### 📖 Documentation

| Guide | Description |
|-------|-------------|
| [GUIDE_PRODUCTION.md](./GUIDE_PRODUCTION.md) | Pipeline de production complet |
| [GUIDE_COLAB.md](./GUIDE_COLAB.md) | Guide utilisation Colab |
| [SPECULUM_ROADMAP.md](./SPECULUM_ROADMAP.md) | Roadmap du projet |

### 🔗 Ressources externes

| Ressource | Lien |
|-----------|------|
| Poly Haven HDRi | [polyhaven.com/hdris](https://polyhaven.com/hdris) |
| Mixamo | [mixamo.com](https://www.mixamo.com/) |
| Blender Downloads | [blender.org/download](https://www.blender.org/download/) |



> 📅 **Dernière mise à jour**: EXODUS V2 - Structure Drive
>
> 🏷️ **Version**: 2.0.0
diff --git a/-EXODUS-SPECULUM-/notebooks/SETUP_DRIVE_V2.ipynb b/-EXODUS-SPECULUM-/notebooks/SETUP_DRIVE_V2.ipynb
