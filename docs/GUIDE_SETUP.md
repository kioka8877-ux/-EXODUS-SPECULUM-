# 🔧 GUIDE - Setup des Ressources IA

> **EXODUS-SPECULUM - Configuration initiale des modèles**
>
> Ce guide vous accompagne dans le téléchargement des modèles IA sur Google Drive. Cette opération est à faire **une seule fois**.


## 📋 Table des matières

1. [Pourquoi ce setup?](#1-pourquoi-ce-setup)
2. [Prérequis](#2-prérequis)
3. [Instructions pas à pas](#3-instructions-pas-à-pas)
4. [Structure créée sur Drive](#4-structure-créée-sur-drive)
5. [Modèles téléchargés](#5-modèles-téléchargés)
6. [Troubleshooting](#6-troubleshooting)
7. [Après le setup](#7-après-le-setup)


## 1. Pourquoi ce setup?

| Problème | Solution |
|----------|----------|
| Les modèles IA sont volumineux (~5GB) | Stockage permanent sur Drive |
| Colab réinitialise à chaque session | Les modèles restent sur Drive |
| Téléchargement lent à chaque fois | Téléchargement unique |

**Avantages:**


## 2. Prérequis

| ✅ Requis | Description |
|-----------|-------------|
| Compte Google | Nécessaire pour Colab et Drive |
| ~5GB espace Drive | Pour stocker les modèles |
| Connexion stable | Pour télécharger ~5GB |
| ~30 minutes | Temps de téléchargement |


## 3. Instructions pas à pas

### Étape 1: Ouvrir le notebook

Cliquez sur ce lien pour ouvrir le notebook de setup:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SETUP_RESOURCES.ipynb)

### Étape 2: Autoriser l'accès Drive

1. Exécutez la **Cellule 1** (Montage Drive)
2. Une fenêtre popup apparaît → **Cliquez "Se connecter à Google Drive"**
3. Choisissez votre compte Google
4. Autorisez l'accès

> ⚠️ **Important**: Sans cette autorisation, les modèles seront perdus à chaque session!

### Étape 3: Exécuter les téléchargements

Exécutez chaque cellule **dans l'ordre**:

| Cellule | Contenu | Durée estimée |
|---------|---------|---------------|
| 1 | Montage Drive + Structure | ~10 sec |
| 2 | Depth Anything V2 (~1.3GB) | ~3-5 min |
| 3 | YOLOv8x (~130MB) | ~30 sec |
| 4 | SAM ViT-H (~2.5GB) | ~10-15 min |
| 5 | Real-ESRGAN (~64MB) | ~15 sec |
| 6 | Vérification finale | ~5 sec |

### Étape 4: Vérifier le rapport

La cellule finale affiche un rapport:

```
====================================================
📊 RAPPORT SETUP RESSOURCES
====================================================

✅ Depth Anything V2: 1.32 GB
✅ YOLOv8x: 131.7 MB
✅ SAM ViT-H: 2.56 GB
✅ Real-ESRGAN: 63.9 MB

====================================================
💾 Total installé: 4.07 GB
====================================================

🚀 SETUP COMPLET - Prêt pour production!
```


## 4. Structure créée sur Drive

```
📁 Google Drive
└── 📁 MyDrive
    └── 📁 EXODUS-SPECULUM/
        ├── 📁 SHARED_RESOURCES/
        │   └── 📁 AI_MODELS/
        │       ├── 📁 depth_anything_v2/
        │       │   └── 📄 depth_anything_v2_vitl.pth (1.3GB)
        │       ├── 📁 yolov8/
        │       │   └── 📄 yolov8x.pt (130MB)
        │       ├── 📁 sam/
        │       │   └── 📄 sam_vit_h_4b8939.pth (2.5GB)
        │       ├── 📁 esrgan/
        │       │   └── 📄 RealESRGAN_x4plus.pth (64MB)
        │       └── 📁 rife/
        │           └── (réservé pour interpolation future)
        └── 📁 ASSETSHUB/
            └── (bibliothèque d'assets 3D)
```


## 5. Modèles téléchargés

### Depth Anything V2 ViT-Large
| Propriété | Valeur |
|-----------|--------|
| **Usage** | Estimation de profondeur |
| **Frégate** | F01 SCANNER |
| **Taille** | ~1.3GB |
| **Source** | [HuggingFace](https://huggingface.co/depth-anything/Depth-Anything-V2-Large) |

### YOLOv8x
| Propriété | Valeur |
|-----------|--------|
| **Usage** | Détection d'objets |
| **Frégate** | F01 SCANNER |
| **Taille** | ~130MB |
| **Source** | [Ultralytics](https://github.com/ultralytics/ultralytics) |

### SAM ViT-H (Segment Anything)
| Propriété | Valeur |
|-----------|--------|
| **Usage** | Segmentation précise |
| **Frégate** | F01 SCANNER |
| **Taille** | ~2.5GB |
| **Source** | [Meta AI](https://github.com/facebookresearch/segment-anything) |

### Real-ESRGAN x4plus
| Propriété | Valeur |
|-----------|--------|
| **Usage** | Upscaling 4K |
| **Frégate** | F06 ALCHIMISTE |
| **Taille** | ~64MB |
| **Source** | [xinntao](https://github.com/xinntao/Real-ESRGAN) |


## 6. Troubleshooting

### ❌ Erreur quota Drive

**Symptôme:** `Quota exceeded` ou `Not enough space`

**Solution:**
1. Vérifiez votre espace Drive: [drive.google.com/settings/storage](https://drive.google.com/settings/storage)
2. Libérez au moins 5GB
3. Videz la corbeille Drive (les fichiers supprimés comptent!)
4. Réexécutez le notebook


### ❌ Téléchargement interrompu

**Symptôme:** Cellule bloquée, barre de progression figée

**Solution:**
1. Arrêtez la cellule (bouton Stop ou `Ctrl+M+I`)
2. Supprimez le fichier partiel sur Drive (s'il existe)
3. Réexécutez la même cellule


### ❌ Fichier corrompu

**Symptôme:** Erreur lors du chargement du modèle en production

**Solution:**
1. Supprimez le fichier sur Drive
2. Réexécutez la cellule de téléchargement
3. Vérifiez avec la cellule 7 (Vérification Intégrité)


### ❌ Drive non monté

**Symptôme:** `FileNotFoundError: /content/drive/MyDrive/...`

**Solution:**
1. Réexécutez la Cellule 1 (Montage Drive)
2. Acceptez les permissions dans le popup
3. Continuez avec les autres cellules


### ❌ Timeout Colab

**Symptôme:** Session déconnectée pendant le téléchargement

**Solution:**
1. Reconnectez-vous à Colab
2. Réexécutez la Cellule 1 (Montage Drive)
3. Les modèles déjà téléchargés seront détectés automatiquement
4. Continuez avec les cellules restantes


## 7. Après le setup

### ✅ Setup terminé avec succès?

Vous êtes prêt pour la production! Consultez:

📖 **[GUIDE_PRODUCTION.md](./GUIDE_PRODUCTION.md)** - Guide du pipeline complet

### 📂 Fichiers de référence

| Fichier | Description |
|---------|-------------|
| [CORE_CONFIG/paths.py](../CORE_CONFIG/paths.py) | Chemins des modèles |
| [FRIGATE_01_SCANNER/CODEBASE/segmenter.py](../FRIGATE_01_SCANNER/CODEBASE/segmenter.py) | Utilisation SAM |
| [FRIGATE_01_SCANNER/CODEBASE/depth_estimator.py](../FRIGATE_01_SCANNER/CODEBASE/depth_estimator.py) | Utilisation Depth |

### 🔗 Liens rapides notebooks

| Notebook | Description |
|----------|-------------|
| [SETUP_RESOURCES.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SETUP_RESOURCES.ipynb) | Ce setup (une fois) |
| [SPECULUM_COLAB_TEMPLATE.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb) | Pipeline complet |


> 📅 **Dernière mise à jour**: Phase 2.5B - Setup Resources
>
> 🏷️ **Version**: 1.0.0
new file mode 100644
++ b/-EXODUS-SPECULUM-/notebooks/SETUP_RESOURCES.ipynb
{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "toc_visible": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
