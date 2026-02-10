# 🚀 GUIDE PRODUCTION - Lancement Pipeline EXODUS-SPECULUM

> **EXODUS-SPECULUM - Pipeline Complet en Production**
>
> Ce guide vous accompagne pour lancer le pipeline complet sur Google Colab après validation des tests.


## 📋 Table des matières

1. [Prérequis](#1-prérequis)
2. [Lien Direct Colab](#2-lien-direct-colab)
3. [Cellules Détaillées (6 cellules)](#3-cellules-détaillées)
4. [Configuration Production](#4-configuration-production)
5. [Flux Pipeline (8 Frégates)](#5-flux-pipeline)
6. [Temps Estimés](#6-temps-estimés)
7. [Troubleshooting](#7-troubleshooting)
8. [Checklist Production](#8-checklist-production)
9. [Liens Rapides](#9-liens-rapides)


## 1. Prérequis

### ✅ Tests Validés

Avant de lancer en production, assurez-vous d'avoir exécuté avec succès le notebook de tests:

| Validation | Référence |
|------------|-----------|
| 📘 Tests Unitaires | Voir [GUIDE_COLAB.md](./GUIDE_COLAB.md) - Partie A |
| 📗 Golden Samples | Voir [GUIDE_COLAB.md](./GUIDE_COLAB.md) - Partie B |
| ✅ Checklist P0 | Tous les checks doivent être verts |

### 🔑 Clé API Gemini

Le pipeline utilise **Gemini 1.5 Pro** pour l'analyse IA (Frégate CORTEX).

**Obtenir une clé gratuite:**

1. Aller sur [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Se connecter avec votre compte Google
3. Cliquer sur **"Create API Key"**
4. Copier la clé (format: `AIza...`)
5. ⚠️ **Ne jamais partager cette clé publiquement**

| Quota Gratuit | Limite |
|---------------|--------|
| Requêtes/minute | 60 |
| Requêtes/jour | 1500 |
| Taille image max | 10 MB |

### 📁 Structure Google Drive

Le pipeline utilise une structure de dossiers spécifique dans votre Google Drive:

```
MyDrive/
└── EXODUS-SPECULUM/
    ├── 00_SOURCE/              ← Vidéo source ici
    ├── FRIGATE_00_CORTEX/
    │   ├── INPUT/
    │   └── OUTPUT/             → masterplan.json
    ├── FRIGATE_01_SCANNER/
    │   ├── INPUT/
    │   └── OUTPUT/             → frames/ + depth_maps/
    ├── FRIGATE_02_SCENOGRAPHE/
    │   └── OUTPUT/             → scene_shell.blend
    ├── FRIGATE_03_PROJECTIONNISTE/
    │   └── OUTPUT/             → scene_projected.blend
    ├── FRIGATE_04_LOGISTIQUE/
    │   └── OUTPUT/             → scene_furnished.blend
    ├── FRIGATE_05_DIRECTEUR_PHOTO/
    │   └── OUTPUT/             → scene_animated.blend
    ├── FRIGATE_06_ALCHIMISTE/
    │   └── OUTPUT/             → rendered_frames/
    ├── FRIGATE_07_PORTE_AVIONS/
    │   └── OUTPUT/             → 06_FINAL_PRODUCT/
    ├── SHARED_RESOURCES/
    │   └── AI_MODELS/          ← Modèles IA (auto-download)
    └── ASSETSHUB/              ← Bibliothèque assets 3D
```

> 💡 Les dossiers sont **créés automatiquement** par le notebook si absents.

### 🎬 Vidéo Source

| Critère | Recommandé | Minimum | Maximum |
|---------|------------|---------|---------|
| Format | MP4 (H.264) | MP4, MOV, AVI | - |
| Résolution | 1920×1080 | 480×270 | 7680×4320 |
| FPS | 24-30 | 12 | 60 |
| Durée | 30s - 2min | 10s | 5min |
| Mouvement caméra | Lent et fluide | - | Pas de shaky cam |
| Éclairage | Naturel, uniforme | - | Éviter contre-jour |

**Placement:**
```
MyDrive/EXODUS-SPECULUM/00_SOURCE/ma_video.mp4
```


## 2. Lien Direct Colab

### 🔗 Ouvrir le Pipeline

```
https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb
```

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb)

### ⚙️ Configuration GPU Obligatoire

1. Menu **Runtime** → **Change runtime type**
2. Sélectionner **T4 GPU**
3. Cliquer **Save**

| GPU | VRAM | Recommandé |
|-----|------|------------|
| T4 | 16 GB | ✅ Oui (gratuit) |
| A100 | 40 GB | ✅ Optimal (Colab Pro) |
| CPU | - | ❌ Non supporté |


## 3. Cellules Détaillées

### 📦 Cellule 1: Config & GPU Check

**Ce que ça fait:**

**Durée estimée:** ~5 secondes

**Résultat attendu:**
```
PyTorch: 2.x.x
CUDA disponible: True
GPU: Tesla T4
VRAM: 15.1 GB
```

**Erreurs possibles:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `CUDA disponible: False` | GPU non activé | Runtime → Change runtime type → T4 GPU |
| `ModuleNotFoundError: torch` | Environnement corrompu | Runtime → Factory reset runtime |


### 📁 Cellule 2: Montage Google Drive

**Ce que ça fait:**

**Durée estimée:** ~10-30 secondes (pop-up autorisation)

**Résultat attendu:**
```
📂 Structure du Sanctum EXODUS-SPECULUM:
==================================================
📁 Existant: 00_SOURCE/
📁 Existant: 01_SCANNER_OUT/
✅ Créé: 02_CORTEX_OUT/
...
==================================================
✅ Sanctum prêt: /content/drive/MyDrive/EXODUS-SPECULUM
```

**Erreurs possibles:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| Pop-up bloqué | Navigateur bloque pop-ups | Autoriser pop-ups pour colab.google.com |
| `Permission denied` | Compte Google différent | Déconnecter/reconnecter le bon compte |
| Timeout connexion | Connexion lente | Rafraîchir la page et réessayer |


### 📦 Cellule 3: Installation Dépendances

**Ce que ça fait:**

**Durée estimée:** 3-5 minutes

**Résultat attendu:**
```
🔧 Installation des dépendances...
==================================================
✅ PyTorch + CUDA 11.8
✅ NumPy, OpenCV, Pillow

🔨 Installation Blender headless (bpy)...
⏳ Cette étape peut prendre 2-3 minutes...

==================================================
🔍 Vérification de l'installation bpy...
✅ Blender version: 4.0.0
🔨 BPY IMPORT RÉUSSI - BLENDER HEADLESS OPÉRATIONNEL
```

**Erreurs possibles:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `pip install` échoue | Réseau instable | Réexécuter la cellule |
| `bpy` import error | Dépendances manquantes | Voir section Troubleshooting |
| Timeout | Installation longue | Augmenter patience, réessayer |


### 🔨 Cellule 4: Test Blender GPU

**Ce que ça fait:**

**Durée estimée:** 10-30 secondes

**Résultat attendu:**
```
🔨 Test de Blender Headless avec rendu GPU...
==================================================
✅ Scene reset
✅ Cube créé: TestCube_SPECULUM
✅ Caméra créée: Camera_SPECULUM
✅ Caméra orientée vers le cube
✅ Lumière créée: Sun_SPECULUM
✅ Configuration rendu: CYCLES GPU, 256x256, 8 samples

🔧 Configuration GPU Cycles...
  ✅ Device activé: Tesla T4 (CUDA)
✅ GPU CUDA détecté et activé

🎬 Lancement du rendu test...

==================================================
✅ SUCCÈS: Rendu test sauvegardé
   📍 Chemin: /content/test_render_speculum.png
   📐 Résolution: 256x256
   📦 Taille: 45.2 KB
   ⏱️ Temps: 2.35s

🔨 BLENDER HEADLESS OPÉRATIONNEL
```

**Erreurs possibles:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `⚠️ Aucun GPU CUDA détecté` | GPU non disponible | Vérifier Runtime → T4 GPU |
| Rendu très lent (>60s) | Fallback CPU | Redémarrer runtime avec GPU |
| `ModuleNotFoundError: bpy` | Cellule 3 échouée | Réexécuter cellule 3 |


### 🖼️ Cellule 5: Affichage Rendu Test

**Ce que ça fait:**

**Durée estimée:** ~2 secondes

**Résultat attendu:**

**Erreurs possibles:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Fichier de rendu non trouvé` | Cellule 4 échouée | Réexécuter cellule 4 |
| Image noire | Caméra mal orientée | Bug rare, réexécuter cellule 4 |


### 📊 Cellule 6: Rapport Système

**Ce que ça fait:**

**Durée estimée:** ~3 secondes

**Résultat attendu:**
```
============================================================
          RAPPORT SYSTÈME EXODUS-SPECULUM
============================================================

🐍 Python: 3.10.x

🔥 PyTorch: 2.x.x
   CUDA compilé: 11.8
   CUDA disponible: True

🔨 Blender: 4.0.0

🎮 GPU:
   Nom: Tesla T4
   VRAM Total: 15.1 GB
   VRAM Réservée: 0.50 GB
   VRAM Allouée: 0.00 GB
   VRAM Libre: 14.6 GB

📁 Storage:
   Drive monté: ✅
   Sanctum présent: ✅

============================================================
          CHECKLIST VALIDATION P0
============================================================
   ✅ Python 3.10+
   ✅ PyTorch installé
   ✅ CUDA disponible
   ✅ Blender bpy importé
   ✅ Google Drive monté
   ✅ Sanctum structure
   ✅ Rendu test créé

============================================================
   🚀 SYSTÈME PRÊT POUR EXODUS-SPECULUM
============================================================
```


## 4. Configuration Production

### 🎛️ Variables à Configurer

Une fois les 6 cellules de setup validées, configurez le pipeline:

```python
# ═══════════════════════════════════════════════════
# CONFIGURATION PRODUCTION
# ═══════════════════════════════════════════════════

# Chemin vers la vidéo source
SOURCE_VIDEO = "/content/drive/MyDrive/EXODUS-SPECULUM/00_SOURCE/ma_video.mp4"

# Clé API Gemini (obtenue sur aistudio.google.com/app/apikey)
GEMINI_API_KEY = "AIzaSy..."  # ⚠️ Ne jamais commiter cette clé!

# Mode de production
PRODUCTION_MODE = "CONQUERANT"  # ECLAIREUR | CONQUERANT | SOUVERAIN
```

### 📊 Tableau Comparatif des Modes

| Paramètre | 🔦 ECLAIREUR | ⚔️ CONQUERANT | 👑 SOUVERAIN |
|-----------|--------------|---------------|--------------|
| **Usage** | Tests & Preview | Production Standard | Export Final |
| **Résolution** | 960×540 | 1920×1080 (Full HD) | 3840×2160 (4K) |
| **FPS** | 12 | 24 | 60 |
| **Samples Cycles** | 16 | 64 | 128 |
| **Denoiser** | OpenImageDenoise | OptiX | OptiX |
| **Upscaling** | ❌ Non | ✅ 2x (Real-ESRGAN) | ✅ 2x + Interpolation |
| **Interpolation** | ❌ Non | ❌ Non | ✅ RIFE (24→60fps) |
| **Durée estimée** | ~10 min | ~45 min | ~2h+ |
| **VRAM requise** | 8 GB | 12 GB | 14 GB |
| **Qualité** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommandations:**

| Cas d'usage | Mode recommandé |
|-------------|-----------------|
| Premier test du pipeline | ECLAIREUR |
| Validation créative | ECLAIREUR |
| Production YouTube/TikTok | CONQUERANT |
| Portfolio professionnel | SOUVERAIN |
| Client exigeant | SOUVERAIN |


## 5. Flux Pipeline

### 🚢 Diagramme des 8 Frégates

```
                    EXODUS-SPECULUM PIPELINE
    ═══════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────┐
    │                 📹 00_SOURCE                     │
    │              (Vidéo immobilière)                │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  🧠 F00 CORTEX                                  │
    │  Intelligence IA - Gemini 1.5 Pro              │
    │  → Analyse scène, détection objets             │
    │  → OUTPUT: masterplan.json                     │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  📡 F01 SCANNER                                 │
    │  Extraction vidéo + Depth Estimation           │
    │  → Depth Anything V2, YOLOv8, SAM              │
    │  → OUTPUT: frames/ + depth_maps/               │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  🎭 F02 SCÉNOGRAPHE                             │
    │  Génération Géométrie 3D                       │
    │  → Blob room + ghost proxies                   │
    │  → OUTPUT: scene_shell.blend                   │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  📽️ F03 PROJECTIONNISTE                        │
    │  Camera Projection Mapping                     │
    │  → Textures vidéo sur géométrie 3D             │
    │  → OUTPUT: scene_projected.blend               │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  📦 F04 LOGISTIQUE                              │
    │  Asset Replacement                             │
    │  → Ghost Proxy → Real 3D Assets                │
    │  → OUTPUT: scene_furnished.blend               │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  🎬 F05 DIRECTEUR PHOTO                         │
    │  Camera Animation + Smart-Crop                 │
    │  → Mouvements caméra réalistes                 │
    │  → OUTPUT: scene_animated.blend                │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  ⚗️ F06 ALCHIMISTE                              │
    │  Rendu Cycles + Upscaling IA                   │
    │  → Real-ESRGAN, RIFE                           │
    │  → OUTPUT: rendered_frames/                    │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │  🛫 F07 PORTE-AVIONS                            │
    │  Assemblage Final                              │
    │  → Encodage H.264/HEVC + Audio ASMR            │
    │  → Export multi-plateformes                    │
    │  → OUTPUT: FINAL_SPECULUM_TOUR_4K.mp4          │
    └─────────────────────┬───────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────┐
    │                 📤 06_FINAL_PRODUCT             │
    │  ├── youtube_4k.mp4                            │
    │  ├── instagram_square.mp4                      │
    │  └── tiktok_vertical.mp4                       │
    └─────────────────────────────────────────────────┘
```

### 📝 Détail des Frégates

| Frégate | Rôle | Technologies | Input | Output |
|---------|------|--------------|-------|--------|
| F00 CORTEX | Analyse IA | Gemini 1.5 Pro | keyframes.png | masterplan.json |
| F01 SCANNER | Extraction | Depth Anything V2, YOLOv8 | video.mp4 | frames/, depth_maps/ |
| F02 SCÉNOGRAPHE | Géométrie 3D | Blender, Python | depth_maps/ | scene_shell.blend |
| F03 PROJECTIONNISTE | Projection | Blender Cycles | frames/, scene_shell | scene_projected.blend |
| F04 LOGISTIQUE | Assets | Blender, ASSETSHUB | scene_projected | scene_furnished.blend |
| F05 DIRECTEUR PHOTO | Animation | Blender | scene_furnished | scene_animated.blend |
| F06 ALCHIMISTE | Rendu | Cycles, Real-ESRGAN, RIFE | scene_animated | rendered_frames/ |
| F07 PORTE-AVIONS | Export | FFmpeg, Audio | rendered_frames/ | final_video.mp4 |


## 6. Temps Estimés

### ⏱️ Par Frégate (vidéo 1 minute, 24 FPS source)

| Frégate | 🔦 ECLAIREUR | ⚔️ CONQUERANT | 👑 SOUVERAIN |
|---------|--------------|---------------|--------------|
| F00 CORTEX | 30s | 30s | 30s |
| F01 SCANNER | 2 min | 3 min | 5 min |
| F02 SCÉNOGRAPHE | 1 min | 2 min | 3 min |
| F03 PROJECTIONNISTE | 2 min | 5 min | 10 min |
| F04 LOGISTIQUE | 1 min | 3 min | 5 min |
| F05 DIRECTEUR PHOTO | 30s | 1 min | 2 min |
| F06 ALCHIMISTE | 3 min | 25 min | 60 min |
| F07 PORTE-AVIONS | 1 min | 5 min | 15 min |
| **TOTAL** | **~10 min** | **~45 min** | **~100 min** |

### 📊 Par Durée Vidéo Source (Mode CONQUERANT)

| Durée source | Temps pipeline | Output estimé |
|--------------|----------------|---------------|
| 15 secondes | ~15 min | ~45s rendu |
| 30 secondes | ~25 min | ~90s rendu |
| 1 minute | ~45 min | ~3 min rendu |
| 2 minutes | ~90 min | ~6 min rendu |
| 5 minutes | ~4h | ~15 min rendu |

> ⚠️ **Note:** Les temps incluent le rendu Cycles qui est le goulot d'étranglement principal. Mode SOUVERAIN multiplie par ~2x à cause de l'interpolation RIFE.


## 7. Troubleshooting

### 🔴 CUDA out of memory

**Symptômes:**
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
torch.cuda.OutOfMemoryError
```

**Solutions:**

| Action | Commande/Étape |
|--------|----------------|
| Libérer VRAM | `torch.cuda.empty_cache()` |
| Réduire batch size | Dans config: `BATCH_SIZE = 1` |
| Passer en mode ECLAIREUR | Moins de VRAM requise |
| Redémarrer runtime | Runtime → Restart runtime |
| Vérifier processus | `!nvidia-smi` pour voir usage VRAM |

**Prévention:**
```python
# Ajouter au début du pipeline
import gc
gc.collect()
torch.cuda.empty_cache()
```


### 🔴 Gemini rate limit

**Symptômes:**
```
ResourceExhausted: 429 Too Many Requests
google.api_core.exceptions.ResourceExhausted
```

**Solutions:**

| Action | Détail |
|--------|--------|
| Attendre | Rate limit reset toutes les 60 secondes |
| Réduire fréquence | Espacer les appels API |
| Vérifier quota | [Google AI Studio Dashboard](https://aistudio.google.com/) |
| Nouvelle clé | Créer une autre clé API si limite atteinte |

**Code avec retry:**
```python
import time
from google.api_core.exceptions import ResourceExhausted

def call_gemini_with_retry(prompt, max_retries=3):
    for i in range(max_retries):
        try:
            return model.generate_content(prompt)
        except ResourceExhausted:
            wait_time = (2 ** i) * 10  # 10s, 20s, 40s
            print(f"⏳ Rate limit, attente {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Gemini rate limit exceeded after retries")
```


### 🔴 bpy import error

**Symptômes:**
```
ModuleNotFoundError: No module named 'bpy'
ImportError: libGL.so.1: cannot open shared object file
```

**Solutions:**

| Étape | Commande |
|-------|----------|
| 1. Installer dépendances système | `!apt-get install -y libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1` |
| 2. Réinstaller bpy | `!pip install --force-reinstall bpy==4.0.0` |
| 3. Redémarrer runtime | Runtime → Restart runtime |
| 4. Alternative apt | `!apt-get install -y blender` (puis utiliser en CLI) |

**Test d'import:**
```python
try:
    import bpy
    print(f"✅ Blender {bpy.app.version_string}")
except ImportError as e:
    print(f"❌ {e}")
    print("Réexécuter cellule 3 (Installation Dépendances)")
```


### 🔴 Session timeout / Disconnect

**Symptômes:**
```
Your session crashed after using all available RAM
Runtime disconnected. Click Reconnect.
```

**Solutions:**

| Action | Détail |
|--------|--------|
| Reconnect | Bouton "Reconnect" en haut |
| Anti-idle | Garder l'onglet actif (pas en arrière-plan) |
| Checkpoints | Activer sauvegarde auto toutes les 15 min |
| Colab Pro | Sessions plus longues (jusqu'à 24h) |

**Script anti-déconnexion (à exécuter dans la console JS du navigateur):**
```javascript
function ClickConnect(){
    console.log("Keeping Colab alive...");
    document.querySelector("#connect").click();
}
setInterval(ClickConnect, 60000);
```

**Sauvegarde de progression:**
```python
# À ajouter entre chaque frégate
import json
checkpoint = {
    "last_completed_frigate": "F02_SCENOGRAPHE",
    "timestamp": str(datetime.now()),
    "state": current_state
}
with open(f"{SANCTUM_PATH}/checkpoint.json", "w") as f:
    json.dump(checkpoint, f)
print("💾 Checkpoint sauvegardé")
```


### 🔴 Autres Erreurs Courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `FileNotFoundError` | Chemin incorrect | Vérifier que la vidéo est dans 00_SOURCE/ |
| `Permission denied` | Drive pas monté | Réexécuter cellule 2 |
| `Video codec not supported` | Format incompatible | Convertir en MP4 H.264 |
| `Blender crash` | Scène trop complexe | Réduire résolution/samples |
| `Network error` | Connexion instable | Vérifier WiFi, réessayer |


## 8. Checklist Production

### 📋 Avant de Lancer

```
□ Tests validés (GUIDE_COLAB.md complété)
□ Clé API Gemini obtenue et testée
□ Vidéo source préparée et uploadée dans 00_SOURCE/
□ Format vidéo vérifié (MP4 H.264, résolution OK)
□ Mode de production choisi (ECLAIREUR/CONQUERANT/SOUVERAIN)
□ Temps disponible estimé (voir section 6)
```

### 📋 Setup Colab (Cellules 1-6)

```
□ GPU T4 activé (Runtime → Change runtime type)
□ Cellule 1: Config & GPU Check ✅
□ Cellule 2: Montage Google Drive ✅
□ Cellule 3: Installation Dépendances ✅ (3-5 min)
□ Cellule 4: Test Blender GPU ✅
□ Cellule 5: Affichage Rendu Test ✅
□ Cellule 6: Rapport Système - Tous checks verts ✅
```

### 📋 Configuration Production

```
□ SOURCE_VIDEO path correct
□ GEMINI_API_KEY configurée
□ PRODUCTION_MODE sélectionné
□ Espace Drive suffisant (~10GB pour vidéo 1 min)
```

### 📋 Pendant l'Exécution

```
□ F00 CORTEX: masterplan.json généré
□ F01 SCANNER: frames/ et depth_maps/ créés
□ F02 SCÉNOGRAPHE: scene_shell.blend généré
□ F03 PROJECTIONNISTE: scene_projected.blend généré
□ F04 LOGISTIQUE: scene_furnished.blend généré
□ F05 DIRECTEUR PHOTO: scene_animated.blend généré
□ F06 ALCHIMISTE: rendered_frames/ complet
□ F07 PORTE-AVIONS: vidéo finale exportée
```

### 📋 Après l'Exécution

```
□ Vidéo finale vérifiée dans 06_FINAL_PRODUCT/
□ Qualité visuelle OK (pas d'artefacts)
□ Audio présent (si activé)
□ Variants exportés (YouTube, Instagram, TikTok)
□ Nettoyage fichiers temporaires (optionnel)
```


## 9. Liens Rapides

### 🔗 Notebooks

| Notebook | Description | Lien |
|----------|-------------|------|
| 📘 Tests Unitaires | Validation fonctions de base | [SPECULUM_GOLDEN_TESTS.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_GOLDEN_TESTS.ipynb) |
| 📗 Pipeline Complet | Production complète | [SPECULUM_COLAB_TEMPLATE.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb) |

### 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Documentation principale |
| [GUIDE_COLAB.md](./GUIDE_COLAB.md) | Guide tests et golden samples |
| [SPECULUM_PRD.md](./SPECULUM_PRD.md) | Spécifications techniques |

### 🔑 Ressources Externes

| Ressource | URL |
|-----------|-----|
| 🔑 Clé API Gemini | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| 📊 Google AI Studio | [aistudio.google.com](https://aistudio.google.com/) |
| 💾 Google Drive | [drive.google.com](https://drive.google.com/) |
| 📓 Google Colab | [colab.research.google.com](https://colab.research.google.com/) |

### 🛠️ Dossiers Projet

| Dossier | Contenu |
|---------|---------|
| `CORE_CONFIG/` | Configuration centrale (paths, contracts) |
| `CORE_TOOLS/` | Outils partagés |
| `FRIGATE_XX_*/` | Code de chaque frégate |
| `notebooks/` | Notebooks Colab |
| `tests/` | Tests unitaires |


## 📞 Support

En cas de problème non résolu:

1. **Capture d'écran** de l'erreur complète
2. **Copier** le message d'erreur (texte brut)
3. **Noter** quelle frégate/cellule a échoué
4. **Vérifier** cette documentation (section Troubleshooting)
5. **Contacter** l'équipe technique avec ces informations


> 📅 **Dernière mise à jour**: Phase 2.5B - Production Pipeline
>
> 🏷️ **Version**: 1.0.0