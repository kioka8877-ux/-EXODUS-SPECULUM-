# 🚀 GUIDE COMPLET - Exécution Tests sur Google Colab

> **EXODUS-SPECULUM - Phase 2.5B: Golden Tests Framework**
>
> Ce guide vous permet d'exécuter les tests et générer les golden samples sur Google Colab, même sans expérience technique.

---

## 📋 Table des matières

1. [Prérequis](#1-prérequis)
2. [PARTIE A: Exécuter les Tests](#2-partie-a-exécuter-les-tests)
3. [PARTIE B: Générer les Golden Samples](#3-partie-b-générer-les-golden-samples)
4. [Troubleshooting](#4-troubleshooting)
5. [Checklist Finale](#5-checklist-finale)
6. [Liens Rapides](#6-liens-rapides)

---

## 1. Prérequis

| ✅ Requis | Description |
|-----------|-------------|
| Compte Google | Nécessaire pour accéder à Colab (gratuit) |
| Navigateur moderne | Chrome, Firefox, Safari, Edge (version récente) |
| Connexion internet | Stable, minimum 5 Mbps recommandé |

> 💡 **Astuce**: Si vous êtes déjà connecté à Gmail ou Google Drive, vous êtes prêt !

---

## 2. PARTIE A: Exécuter les Tests

### 📘 Notebook: `run_tests_colab.ipynb`

Ce notebook exécute la suite complète de tests unitaires et d'intégration du projet.

---

### Étape 1: Ouvrir le notebook

#### 🔗 Option rapide (lien direct)

Cliquez sur ce lien:
```
https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/run_tests_colab.ipynb
```

#### 📝 Option manuelle (pas à pas)

```
1. Aller sur colab.research.google.com
2. Cliquer sur "Fichier" → "Ouvrir un notebook"
3. Sélectionner l'onglet "GitHub"
4. Dans le champ de recherche, coller: kioka8877-ux/-EXODUS-SPECULUM-
5. Appuyer sur Entrée
6. Cliquer sur: notebooks/run_tests_colab.ipynb
```

> ⚠️ **Important**: Si Google demande une autorisation, cliquez "Autoriser"

---

### Étape 2: Exécuter les cellules

Pour exécuter une cellule:
- **Clavier**: `Shift + Entrée`
- **Souris**: Cliquer sur le bouton ▶️ à gauche de la cellule

> 🔄 **Exécutez les cellules dans l'ordre, une par une**

---

### 📦 Cellule 1 - Setup Environment

```python
!git clone https://github.com/kioka8877-ux/-EXODUS-SPECULUM-.git
%cd -EXODUS-SPECULUM-
!pip install -q -r tests/requirements-test.txt
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Clone le dépôt GitHub et installe les dépendances (pytest, numpy, opencv, etc.) |
| **Durée estimée** | ~30 secondes |
| **Résultat attendu** | `✅ Environment ready!` |

**Si erreur "Permission denied":**
```
🔄 Solution: Recharger la page (F5) et réessayer
```

**Si erreur "Repository not found":**
```
🔄 Solution: Vérifier que le repo est public ou que vous avez les droits
```

---

### 🧪 Cellule 2 - Unit Tests

```python
!python -m pytest tests/unit/ -v --tb=short
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Lance les 8 fichiers de tests unitaires (F00 à F07) |
| **Durée estimée** | ~1-2 minutes |
| **Résultat attendu** | Liste des tests avec statut PASSED/FAILED |

**Comprendre les résultats:**
```
✅ PASSED  = Test réussi (en vert)
❌ FAILED  = Test échoué (en rouge)
⏭️ SKIPPED = Test ignoré (en jaune)
```

**Exemple de sortie normale:**
```
tests/unit/test_f00_cortex.py::test_masterplan_structure PASSED
tests/unit/test_f01_scanner.py::test_depth_output PASSED
tests/unit/test_f02_scenographe.py::test_layers PASSED
...
==================== 20 passed, 3 skipped in 45.32s ====================
```

---

### 🔗 Cellule 3 - Integration Tests

```python
!python -m pytest tests/integration/ -v --tb=short
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Teste que les frégates communiquent correctement entre elles |
| **Durée estimée** | ~30 secondes |
| **Résultat attendu** | Tests d'intégration passés |

**Ce qui est testé:**
- Communication F00 → F01 (Cortex vers Scanner)
- Transfert de données entre modules
- Cohérence des formats de sortie

---

### 📊 Cellule 4 - All Tests with Report

```python
!python -m pytest tests/ -v --tb=short --json-report --json-report-file=test_report.json
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Lance TOUS les tests et génère un rapport JSON détaillé |
| **Durée estimée** | ~2-3 minutes |
| **Résultat attendu** | Tableau récapitulatif des résultats |

**Résultat attendu:**
```
═══════════════════════════════════════════════════════════════
📊 RÉSULTATS DES TESTS
═══════════════════════════════════════════════════════════════
   Total:   25
   Passed:  23 ✅
   Failed:  0 ❌
   Skipped: 2 ⏭️
   Duration: 45.32s
═══════════════════════════════════════════════════════════════
```

> 🎯 **Objectif**: 0 FAILED = Pipeline validé !

**Si des tests échouent:**
```
❌ Tests échoués:
   - tests/unit/test_f01_scanner.py::test_depth_format
     AssertionError: Expected uint16, got float32...
```
→ Noter le nom du test et consulter la section Troubleshooting

---

### ✅ Cellule 5 - Quick Validation

```python
# Validation rapide des imports et contrats
from CORE_CONFIG.output_contracts import DELIVERY_PROFILES, FRIGATE_CONTRACTS
from tests.validators import JSONValidator, DepthValidator, VideoValidator
from tests.mocks import generate_mock_depth, generate_mock_masterplan
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Vérifie que tous les imports et modules fonctionnent |
| **Durée estimée** | ~5 secondes |
| **Résultat attendu** | Tous les ✅ verts |

**Résultat attendu:**
```
🔍 Quick Validation Check

✅ output_contracts: 8 frigates, 3 profiles
✅ validators: All importable
✅ mocks: All importable
✅ golden samples: masterplan exists = True

✅ Quick validation complete!
```

**Si un ❌ apparaît:**
| Message | Cause | Solution |
|---------|-------|----------|
| `❌ output_contracts` | Fichier manquant | Vérifier le clone du repo |
| `❌ validators` | Import cassé | Réinstaller les dépendances |
| `❌ golden samples` | Samples manquants | Exécuter PARTIE B d'abord |

---

### 🎯 Cellule 6 - Specific Tests (optionnel)

```python
# Tests F01 Scanner seulement
!python -m pytest tests/unit/test_f01_scanner.py -v --tb=line

# Tests F07 Porte-Avions seulement
!python -m pytest tests/unit/test_f07_porte_avions.py -v --tb=line
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Exécute uniquement les tests F01 et F07 |
| **Durée estimée** | ~20 secondes |
| **Utilité** | Debug si un module spécifique pose problème |

> 💡 **Quand utiliser**: Si un test échoue dans la cellule 4, vous pouvez isoler le module problématique ici.

---

### 📋 Cellule 7 - Coverage Summary

```python
# Résumé de couverture des tests
from pathlib import Path
unit_tests = list(Path("tests/unit").glob("test_*.py"))
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Compte et liste tous les fichiers de tests |
| **Durée estimée** | ~2 secondes |
| **Résultat attendu** | Liste complète des fichiers de tests |

**Résultat attendu:**
```
📋 Test Coverage Summary
══════════════════════════════════════════════════

Unit Tests: 8 files
   - test_f00_cortex.py
   - test_f01_scanner.py
   - test_f02_scenographe.py
   - test_f03_projectionniste.py
   - test_f04_logistique.py
   - test_f05_directeur_photo.py
   - test_f06_alchimiste.py
   - test_f07_porte_avions.py

Integration Tests: 2 files
   - test_pipeline_integration.py
   - test_frigate_communication.py

📊 Total test functions: ~25
══════════════════════════════════════════════════
```

---

## 3. PARTIE B: Générer les Golden Samples

### 📘 Notebook: `generate_golden_samples.ipynb`

Ce notebook génère les échantillons de référence (golden samples) utilisés pour valider les tests.

---

### Étape 1: Ouvrir le notebook

#### 🔗 Lien direct
```
https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/generate_golden_samples.ipynb
```

---

### 📦 Cellule 1 - Setup

```python
!git clone https://github.com/kioka8877-ux/-EXODUS-SPECULUM-.git
%cd -EXODUS-SPECULUM-
!pip install -q numpy opencv-python-headless Pillow
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Clone le repo et installe numpy, OpenCV et Pillow |
| **Durée estimée** | ~30 secondes |
| **Résultat attendu** | Aucun message d'erreur, passage à la suite |

---

### 🖼️ Cellule 2 - Mock Frame

```python
def create_test_frame(width=960, height=540):
    """Génère une frame RGB simulant un intérieur."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    # Gradient simulant un intérieur
    ...
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Génère une image de test 960×540 pixels simulant un intérieur |
| **Durée estimée** | ~2 secondes |
| **Fichier créé** | `tests/golden/input/test_frame_001.png` |

**Résultat attendu:**
```
✅ Frame créée: (540, 960, 3)
   Dtype: uint8
   Range: [100, 200]
```

**Détails techniques:**
- Format: PNG (RGB 8-bit)
- Résolution: 960×540 (aspect 16:9)
- Contenu: Gradient simulant un éclairage d'intérieur

---

### 📏 Cellule 3 - Mock Depth Map

```python
def create_test_depth(width=960, height=540):
    """Génère une depth map 16-bit simulant une pièce."""
    depth = (1 - y * 0.7) * 50000 + 10000
    ...
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Génère une carte de profondeur 16-bit simulant une pièce |
| **Durée estimée** | ~2 secondes |
| **Fichier créé** | `tests/golden/f01_depth/test_depth_001.npz` |

**Résultat attendu:**
```
✅ Depth créée: (540, 960)
   Dtype: uint16
   Range: [8234, 61203]
   Mean: 35421.3
   Std: 12543.7
```

**Détails techniques:**
- Format: NPZ compressé (NumPy archive)
- Type: uint16 (16-bit unsigned integer)
- Range: 0-65535 (distance en mm typiquement)
- Contenu: Gradient de profondeur avec bruit réaliste

---

### 📦 Cellule 4 - Batch Generation

```python
BATCH_SIZE = 5
for i in range(BATCH_SIZE):
    frame = create_test_frame()
    depth = create_test_depth()
    ...
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Génère 5 paires frame/depth avec variations aléatoires |
| **Durée estimée** | ~10 secondes |
| **Fichiers créés** | 5 frames + 5 depth maps |

**Résultat attendu:**
```
🔄 Generating 5 frame/depth pairs...
   [1/5] Generated pair 001
   [2/5] Generated pair 002
   [3/5] Generated pair 003
   [4/5] Generated pair 004
   [5/5] Generated pair 005

✅ Batch generation complete!
```

**Fichiers générés:**
```
tests/golden/input/
├── test_frame_001.png
├── test_frame_002.png
├── test_frame_003.png
├── test_frame_004.png
└── test_frame_005.png

tests/golden/f01_depth/
├── test_depth_001.npz
├── test_depth_002.npz
├── test_depth_003.npz
├── test_depth_004.npz
└── test_depth_005.npz
```

---

### ✅ Cellule 5 - Validation

```python
from tests.validators.depth_validator import DepthValidator
validator = DepthValidator("tests/contracts/depth_contract.json")
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Valide que les samples générés respectent les contrats |
| **Durée estimée** | ~5 secondes |
| **Résultat attendu** | Tous les fichiers VALID |

**Résultat attendu:**
```
🔍 Validating 5 depth files...

✅ test_depth_001.npz: VALID
✅ test_depth_002.npz: VALID
✅ test_depth_003.npz: VALID
✅ test_depth_004.npz: VALID
✅ test_depth_005.npz: VALID

📊 Results: 5 passed, 0 failed
```

**Si un fichier est INVALID:**
```
❌ test_depth_003.npz: INVALID - ['dtype must be uint16', 'shape mismatch']
```
→ Re-exécuter la cellule 3 et 4

---

### 📤 Cellule 6 - Git Status

```python
!git add tests/golden/
!git status
```

| 📌 Info | Détail |
|---------|--------|
| **Ce que ça fait** | Montre les fichiers prêts à être commités |
| **Durée estimée** | ~2 secondes |
| **Résultat attendu** | Liste des nouveaux fichiers golden |

**Résultat attendu:**
```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   tests/golden/f01_depth/test_depth_001.npz
        new file:   tests/golden/f01_depth/test_depth_002.npz
        ...
        new file:   tests/golden/input/test_frame_001.png
        ...

═══════════════════════════════════════════════════════════════
⚠️  Pour commit, exécutez manuellement:
!git commit -m "TST: Add golden samples"
!git push
═══════════════════════════════════════════════════════════════
```

> ⚠️ **Note**: Le push vers GitHub nécessite une authentification. Contactez un administrateur si besoin.

---

## 4. Troubleshooting

### 🔧 Erreurs fréquentes et solutions

| Erreur | Cause | Solution |
|--------|-------|----------|
| `ModuleNotFoundError: No module named 'CORE_CONFIG'` | Le notebook n'est pas dans le bon répertoire | Vérifier que `%cd -EXODUS-SPECULUM-` a bien fonctionné. Re-exécuter la cellule 1 |
| `Permission denied` | Session Colab expirée ou problème de droits | Recharger la page (F5) et réessayer |
| `CUDA out of memory` | Erreur GPU (faux positif) | Ce notebook n'utilise pas le GPU - ignorer ce message |
| Tests `SKIPPED` | Modules ML non installés | Normal pour les tests nécessitant GPU/ML. Ne pas s'inquiéter |
| `FileNotFoundError: test_masterplan.json` | Golden samples manquants | Exécuter `generate_golden_samples.ipynb` **d'abord** |
| `ModuleNotFoundError: No module named 'pytest'` | Dépendances non installées | Re-exécuter la cellule 1 (Setup) |
| `Repository not found` | Repo privé ou URL incorrecte | Vérifier l'URL du repo GitHub |
| `JSONDecodeError` | Fichier JSON corrompu | Supprimer et régénérer le fichier concerné |
| `ImportError: cv2` | OpenCV non installé | Exécuter: `!pip install opencv-python-headless` |
| `AssertionError: dtype mismatch` | Mauvais format de données | Vérifier que les arrays sont en uint16 (depth) ou uint8 (frame) |

---

### 🔄 Réinitialisation complète

Si rien ne fonctionne, réinitialisez l'environnement:

```python
# Supprimer le repo cloné
!rm -rf -EXODUS-SPECULUM-

# Re-cloner depuis zéro
!git clone https://github.com/kioka8877-ux/-EXODUS-SPECULUM-.git
%cd -EXODUS-SPECULUM-
!pip install -r tests/requirements-test.txt

print("✅ Environnement réinitialisé!")
```

---

### 💡 Astuces Colab

| Astuce | Description |
|--------|-------------|
| **Runtime** | Menu "Runtime" → "Restart runtime" pour réinitialiser Python |
| **GPU** | Non requis pour les tests (CPU suffit) |
| **Timeout** | Colab se déconnecte après ~90 min d'inactivité |
| **Stockage** | Les fichiers sont perdus après déconnexion |
| **Sauvegarde** | Télécharger les rapports importants avant de quitter |

---

## 5. Checklist Finale

Copiez cette checklist et cochez au fur et à mesure:

```markdown
## ✅ Checklist Validation EXODUS-SPECULUM

### Tests exécutés (run_tests_colab.ipynb):
- [ ] Notebook ouvert sur Colab
- [ ] Cellule 1 (Setup) - "✅ Environment ready!"
- [ ] Cellule 2 (Unit Tests) - __ passed, __ failed
- [ ] Cellule 3 (Integration) - __ passed
- [ ] Cellule 4 (Report) - Total: __ | Passed: __ | Failed: __
- [ ] Cellule 5 (Quick Validation) - Tous ✅
- [ ] Cellule 6 (Specific Tests) - Optionnel ✓
- [ ] Cellule 7 (Coverage) - __ fichiers de tests

### Golden Samples (generate_golden_samples.ipynb):
- [ ] Notebook ouvert sur Colab
- [ ] Cellule 1 (Setup) ✓
- [ ] Cellule 2 (Mock Frame) - Frame créée
- [ ] Cellule 3 (Mock Depth) - Depth créée
- [ ] Cellule 4 (Batch) - 5 paires générées
- [ ] Cellule 5 (Validation) - 5 passed, 0 failed
- [ ] Cellule 6 (Git Status) - Fichiers listés

### Résultat final:
- [ ] 0 FAILED = ✅ Pipeline validé
- [ ] Rapport JSON sauvegardé ou screenshot pris
- [ ] Date de validation: ____/____/______
- [ ] Validé par: _________________
```

---

## 6. Liens Rapides

### 🔗 Liens directs Colab

| Notebook | Lien | Usage |
|----------|------|-------|
| **Tests** | [run_tests_colab.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/run_tests_colab.ipynb) | Exécuter la suite de tests |
| **Golden Samples** | [generate_golden_samples.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/generate_golden_samples.ipynb) | Générer les échantillons de référence |
| **Pipeline complet** | [SPECULUM_COLAB_TEMPLATE.ipynb](https://colab.research.google.com/github/kioka8877-ux/-EXODUS-SPECULUM-/blob/main/notebooks/SPECULUM_COLAB_TEMPLATE.ipynb) | Pipeline complet (⚠️ GPU requis) |

---

### 📚 Ressources supplémentaires

| Ressource | Description |
|-----------|-------------|
| [README.md](../README.md) | Documentation principale du projet |
| [tests/](../tests/) | Dossier des tests |
| [CORE_CONFIG/](../CORE_CONFIG/) | Configuration centrale |

---

### 📞 Support

En cas de problème non résolu:

1. **Capture d'écran** de l'erreur
2. **Copier** le message d'erreur complet
3. **Noter** quelle cellule a échoué
4. **Contacter** l'équipe technique avec ces informations

---

> 📅 **Dernière mise à jour**: Phase 2.5B - Golden Tests Framework
>
> 🏷️ **Version**: 1.0.0
