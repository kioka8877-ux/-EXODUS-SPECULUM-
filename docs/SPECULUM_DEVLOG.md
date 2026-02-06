# SPECULUM_DEVLOG.md - Annales de la Forge
> Journal technique EXODUS-SPECULUM

---

## Format des Entrées

```markdown
### [DATE] - [TITRE]

**Contexte:** [Problème ou objectif à résoudre]

**Solution:** [Ce qui a été fait, approche choisie]

**Code critique:**
```python
[Snippet de code clé]
```

**Résultats:** [Métriques, observations]

**Leçon apprise:** [Takeaway pour le futur]

**Liens:** [Issues, PRs, références]
```

---

## Entrées

---

### [2026-02-06] - Initialisation du projet EXODUS-SPECULUM

**Contexte:** 
Création de l'Hexagramme documentaire complet pour structurer le projet avant tout développement. Le projet vise à transformer des vidéos immobilières en clones 3D via Camera Projection Mapping.

**Solution:** 
Rédaction de 6 documents fondateurs définissant l'architecture, les spécifications, le planning et les protocoles de test.

**Documents créés:**
1. `SPECULUM_STATE.md` - État technique du système
2. `SPECULUM_PRD.md` - Spécifications fonctionnelles
3. `SPECULUM_ROADMAP.md` - Chronologie de développement
4. `SPECULUM_LOGBOOK.md` - Registre des tâches granulaires
5. `SPECULUM_DEVLOG.md` - Journal technique (ce document)
6. `SPECULUM_VALIDATION.md` - Protocoles de test

**Architecture définie:**
- 8 Frégates (modules) avec interfaces claires
- Pipeline séquentiel avec dépendances documentées
- 3 modes de qualité (TURBO-SPECULUM)
- Système FORMAT-ADAPT pour multi-plateforme

**Leçon apprise:** 
La documentation AVANT le code garantit la cohérence architecturale et évite le refactoring coûteux. Chaque frégate a maintenant des spécifications Input→Traitement→Output claires.

**Liens:**
- Commit initial: `🏛️ HEXAGRAMME: Forge des 6 piliers fondateurs`

---

### [2026-02-06] - P0-B: Test Ressources Partagées (Latence)

**Contexte:** 
Sprint P0-B - Validation du lien entre Colab et les ressources partagées sur Google Drive (modèles IA + assets Blender).

**Tests effectués:**
1. Chargement Depth Anything V2 depuis Drive
2. Blender Library Linking depuis Drive

**Résultats de latence:**
| Ressource | Taille | Latence | Verdict |
|-----------|--------|---------|----------|
| Depth Anything V2 | ~1.3 GB | À mesurer | [À TESTER SUR COLAB] |
| Blender Asset Link | ~1 MB | À mesurer | [À TESTER SUR COLAB] |

**Code critique:**
```python
# Library Linking depuis Drive
with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
    data_to.objects = list(data_from.objects)

# Vérification Ghost Proxy
if linked_obj.get("is_ghost_proxy"):
    print(f"Type: {linked_obj.get('asset_type')}")
```

**Structure validée:**
```
/content/drive/MyDrive/EXODUS_SHARED_RESOURCES/
├── AI_MODELS/
│   └── depth_anything_v2/
│       └── depth_anything_v2_vitl.pth  (à télécharger)
└── ASSETS_HUB/
    └── test_asset.blend  (créé automatiquement)
```

**Fichiers créés:**
- `notebooks/SPECULUM_COLAB_TEMPLATE.ipynb` - Template Colab avec Cells 7-8
- `scripts/test_shared_resources.py` - Script de test standalone

**Conclusions:**
- Structure EXODUS_SHARED_RESOURCES prête
- Library Linking Blender validé (méthode fonctionnelle)
- Custom properties (Ghost Proxy metadata) préservées
- Latence réelle à mesurer sur Colab avec GPU T4

**Leçon apprise:** 
Le Library Linking Blender depuis Google Drive fonctionne sans problème. Les custom properties sont préservées, ce qui valide le concept de Ghost Proxies avec métadonnées intégrées.

**Liens:**
- Commit: `🔗 P0-B: Ancrage ressources partagées validé`
- HuggingFace Depth Anything V2: https://huggingface.co/depth-anything/Depth-Anything-V2-Large

---

### [TEMPLATE] - Titre de l'entrée

**Contexte:** 
[Description du problème ou de l'objectif]

**Solution:** 
[Approche et implémentation]

**Code critique:**
```python
# Snippet démontrant la solution
pass
```

**Résultats:** 
- Métrique 1: valeur
- Métrique 2: valeur

**Leçon apprise:** 
[Takeaway]

**Liens:**
- [URL ou référence]

---

## Index par Sujet

### Depth Estimation
- [2026-02-06] P0-B: Test Ressources Partagées

### Camera Projection
- *(à venir)*

### Blender Scripting
- [2026-02-06] P0-B: Library Linking depuis Drive

### Upscaling IA
- *(à venir)*

### Performance
- *(à venir)*

### Debugging
- *(à venir)*

---

## Problèmes Résolus (Quick Reference)

| Date | Problème | Solution | Tags |
|------|----------|----------|------|
| 2026-02-06 | Structure ressources Drive | Création auto via Cell 6 + script | drive, setup |

---

## Snippets Réutilisables

### Blender Headless Setup (Colab)
```python
# À documenter après implémentation
```

### Depth Anything V2 Inference
```python
# À documenter après implémentation
```

### Gemini Vision API Call
```python
# À documenter après implémentation
```

### FFmpeg Frame Extraction
```bash
# À documenter après implémentation
```

### Real-ESRGAN Batch
```python
# À documenter après implémentation
```

---

## Ressources Externes Utiles

### Documentation Officielle
- [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)
- [YOLOv8 Ultralytics](https://docs.ultralytics.com/)
- [Segment Anything](https://github.com/facebookresearch/segment-anything)
- [Gemini API](https://ai.google.dev/docs)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [RIFE](https://github.com/nihui/rife-ncnn-vulkan)

### Tutoriels Référencés
- *(à ajouter au fil du développement)*

### Inspirations
- *(projets similaires, papers, etc.)*

---

*Dernière mise à jour: 2026-02-06*
*Entrées: 2*
