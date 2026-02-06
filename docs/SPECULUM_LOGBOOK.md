# SPECULUM_LOGBOOK.md - Registre des Étapes
> Suivi granulaire des tâches EXODUS-SPECULUM

---

## Légende

| Symbole | Signification |
|---------|---------------|
| `[ ]` | À faire |
| `[~]` | En cours |
| `[x]` | Complété |
| `[!]` | Bloqué |
| `[-]` | Annulé |

---

## Phase 0: Fondations

### P0 - Setup & Documentation

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| P0-001 | Créer structure dossiers repository | [ ] | - | - | - | /docs, /src, /assets |
| P0-002 | Rédiger README.md projet | [ ] | - | - | - | Overview + quickstart |
| P0-003 | Configurer .gitignore | [ ] | - | - | - | Python, Blender, Colab |
| P0-004 | Rédiger SPECULUM_STATE.md | [x] | Vulkan | 2026-02-06 | 2026-02-06 | ✅ |
| P0-005 | Rédiger SPECULUM_PRD.md | [x] | Vulkan | 2026-02-06 | 2026-02-06 | ✅ |
| P0-006 | Rédiger SPECULUM_ROADMAP.md | [x] | Vulkan | 2026-02-06 | 2026-02-06 | ✅ |
| P0-007 | Rédiger SPECULUM_LOGBOOK.md | [~] | Vulkan | 2026-02-06 | - | En cours |
| P0-008 | Rédiger SPECULUM_DEVLOG.md | [ ] | - | - | - | |
| P0-009 | Rédiger SPECULUM_VALIDATION.md | [ ] | - | - | - | |
| P0-010 | Créer template Colab de base | [ ] | - | - | - | Notebook vide fonctionnel |
| P0-011 | Script installation dépendances | [ ] | - | - | - | install.sh ou cell Colab |
| P0-012 | Setup Blender headless sur Colab | [ ] | - | - | - | bpy installation |
| P0-013 | Test import bpy | [ ] | - | - | - | Validation setup |
| P0-014 | Test Gemini API integration | [ ] | - | - | - | API key + hello world |
| P0-015 | Structure dossiers ASSETSHUB | [ ] | - | - | - | Sur Google Drive |
| P0-016 | Créer vidéo source test | [ ] | - | - | - | 30sec, 1080p, intérieur |

---

## Phase 1: Proof of Concept

### F01 - SCANNER

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F01-001 | Script extraction frames FFmpeg | [ ] | - | - | - | ffmpeg -vf fps=2 |
| F01-002 | Paramétrer fps extraction | [ ] | - | - | - | Variable configurable |
| F01-003 | Gérer formats vidéo multiples | [ ] | - | - | - | mp4, mov, avi |
| F01-004 | Intégration Depth Anything V2 | [ ] | - | - | - | Via pip + model DL |
| F01-005 | Download modèle ViT-Large | [ ] | - | - | - | ~1.3GB |
| F01-006 | Inference depth single frame | [ ] | - | - | - | Test unitaire |
| F01-007 | Batch inference depth | [ ] | - | - | - | Toutes les frames |
| F01-008 | Export PNG 16-bit | [ ] | - | - | - | Précision depth |
| F01-009 | Optimisation VRAM depth | [ ] | - | - | - | Batch size tuning |
| F01-010 | Intégration YOLOv8 | [ ] | - | - | - | pip install ultralytics |
| F01-011 | Download modèle YOLOv8x | [ ] | - | - | - | ~130MB |
| F01-012 | Detection single frame | [ ] | - | - | - | Test unitaire |
| F01-013 | Batch detection | [ ] | - | - | - | Toutes les frames |
| F01-014 | Filtrer classes pertinentes | [ ] | - | - | - | furniture, person, etc. |
| F01-015 | Intégration SAM | [ ] | - | - | - | segment-anything |
| F01-016 | Download modèle SAM ViT-H | [ ] | - | - | - | ~2.4GB |
| F01-017 | Segmentation via YOLO prompts | [ ] | - | - | - | Point coords from bbox |
| F01-018 | Export masks PNG binaires | [ ] | - | - | - | Per object |
| F01-019 | Créer schema spatial_data.json | [ ] | - | - | - | JSON schema validation |
| F01-020 | Export spatial_data.json | [ ] | - | - | - | Agrégation toutes données |
| F01-021 | Tests unitaires F01 | [ ] | - | - | - | Pytest ou manual |
| F01-022 | Documentation F01 | [ ] | - | - | - | Usage + API |

### F02 - CORTEX

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F02-001 | Setup google-generativeai | [ ] | - | - | - | pip install |
| F02-002 | Gestion API key secure | [ ] | - | - | - | Colab secrets |
| F02-003 | Sélection keyframes automatique | [ ] | - | - | - | 0%, 50%, 100% + rotation |
| F02-004 | Détection rotation camera | [ ] | - | - | - | Via optical flow ou depth diff |
| F02-005 | Prompt engineering v1 | [ ] | - | - | - | Room analysis basic |
| F02-006 | Prompt engineering v2 | [ ] | - | - | - | Dimensions estimation |
| F02-007 | Prompt engineering v3 | [ ] | - | - | - | Materials detection |
| F02-008 | Prompt engineering v4 | [ ] | - | - | - | POI identification |
| F02-009 | Parse Gemini response | [ ] | - | - | - | JSON extraction |
| F02-010 | Validation response schema | [ ] | - | - | - | jsonschema |
| F02-011 | Retry logic rate limits | [ ] | - | - | - | 60 QPM handling |
| F02-012 | Caching responses | [ ] | - | - | - | Éviter re-calls |
| F02-013 | Créer schema masterplan.json | [ ] | - | - | - | Définition complète |
| F02-014 | Export masterplan.json | [ ] | - | - | - | Merge toutes analyses |
| F02-015 | POI heatmap generation | [ ] | - | - | - | 32x32 grid |
| F02-016 | Tests unitaires F02 | [ ] | - | - | - | Mock API responses |
| F02-017 | Documentation F02 | [ ] | - | - | - | Prompts + usage |

### F03 - SCÉNOGRAPHE

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F03-001 | Script Blender baseline | [x] | Capy | 2026-02-06 | 2026-02-06 | bpy.ops basic |
| F03-002 | Créer plane subdivisé | [x] | Capy | 2026-02-06 | 2026-02-06 | 512x512 faces |
| F03-003 | Appliquer displacement modifier | [x] | Capy | 2026-02-06 | 2026-02-06 | Depth texture |
| F03-004 | Calibrer displacement strength | [ ] | - | - | - | Tests visuels |
| F03-005 | Créer 6 surfaces (box room) | [x] | Capy | 2026-02-06 | 2026-02-06 | Floor, walls, ceiling |
| F03-006 | Orienter surfaces correctement | [x] | Capy | 2026-02-06 | 2026-02-06 | Normals vers intérieur |
| F03-007 | Système proxy cubes | [x] | Capy | 2026-02-06 | 2026-02-06 | Furniture boxes |
| F03-008 | Système proxy cylindres | [x] | Capy | 2026-02-06 | 2026-02-06 | Lamps, vases |
| F03-009 | Positionner proxies via masterplan | [x] | Capy | 2026-02-06 | 2026-02-06 | Coordinates mapping |
| F03-010 | Tagger proxies ghost_proxy | [x] | Capy | 2026-02-06 | 2026-02-06 | Custom property |
| F03-011 | Exporter scene_shell.blend | [x] | Capy | 2026-02-06 | 2026-02-06 | Save file |
| F03-012 | Organiser collections | [x] | Capy | 2026-02-06 | 2026-02-06 | ROOM_SHELL, PROXIES |
| F03-013 | Embed metadata dans .blend | [x] | Capy | 2026-02-06 | 2026-02-06 | masterplan reference |
| F03-014 | Tests unitaires F03 | [ ] | - | - | - | Geometry validation |
| F03-015 | Documentation F03 | [ ] | - | - | - | Blender scripting |

### F04 - PROJECTIONNISTE

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F04-001 | Créer camera Blender | [ ] | - | - | - | bpy.ops.object |
| F04-002 | Positionner camera estimée | [ ] | - | - | - | From video metadata |
| F04-003 | UV Project from View single | [ ] | - | - | - | Un keyframe |
| F04-004 | UV Project multi-keyframes | [ ] | - | - | - | 3 UV maps |
| F04-005 | Créer texture nodes | [ ] | - | - | - | ShaderNodeTexImage |
| F04-006 | Lier UV maps aux textures | [ ] | - | - | - | ShaderNodeUVMap |
| F04-007 | Créer mix shader nodes | [ ] | - | - | - | Blending 3 projections |
| F04-008 | Implémenter weight drivers | [ ] | - | - | - | camera_progress var |
| F04-009 | Driver weight_frame0 | [ ] | - | - | - | max(0, 1-p*2) |
| F04-010 | Driver weight_frame50 | [ ] | - | - | - | 1-abs(p-0.5)*2 |
| F04-011 | Driver weight_frame100 | [ ] | - | - | - | max(0, p*2-1) |
| F04-012 | Edge feathering shader | [ ] | - | - | - | Gradient falloff |
| F04-013 | Appliquer material aux surfaces | [ ] | - | - | - | Assign to all |
| F04-014 | Exporter scene_projected.blend | [ ] | - | - | - | Save file |
| F04-015 | Tests visuels projection | [ ] | - | - | - | Render preview |
| F04-016 | Tests unitaires F04 | [ ] | - | - | - | UV validation |
| F04-017 | Documentation F04 | [ ] | - | - | - | Projection math |

---

## Phase 2: Core Pipeline

### F05 - LOGISTIQUE

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F05-001 | Structure ASSETSHUB | [ ] | - | - | - | Dossiers par type |
| F05-002 | Collecter assets gratuits | [ ] | - | - | - | BlenderKit, etc. |
| F05-003 | Standardiser naming assets | [ ] | - | - | - | Convention définie |
| F05-004 | Système détection ghost_proxy | [ ] | - | - | - | Scan objects |
| F05-005 | Algorithm matching dimensions | [ ] | - | - | - | Similarity score |
| F05-006 | Algorithm matching type | [ ] | - | - | - | Category match |
| F05-007 | Linked asset loading | [ ] | - | - | - | bpy.data.libraries |
| F05-008 | Positionnement asset | [ ] | - | - | - | Match proxy transform |
| F05-009 | Masquer proxy après replace | [ ] | - | - | - | hide_render, hide_viewport |
| F05-010 | Système LOD | [ ] | - | - | - | 3 levels |
| F05-011 | LOD drivers distance | [ ] | - | - | - | Camera distance |
| F05-012 | Fallback si no match | [ ] | - | - | - | Keep proxy |
| F05-013 | Exporter scene_furnished.blend | [ ] | - | - | - | Save file |
| F05-014 | Tests unitaires F05 | [ ] | - | - | - | Asset loading |
| F05-015 | Documentation F05 | [ ] | - | - | - | ASSETSHUB format |

### F06 - DIRECTEUR PHOTO

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F06-001 | Détection ratio source | [ ] | - | - | - | Auto detect |
| F06-002 | Mapping format destination | [ ] | - | - | - | Platform selection |
| F06-003 | Calcul sensor shift | [ ] | - | - | - | POI centering |
| F06-004 | Appliquer shift_x, shift_y | [ ] | - | - | - | Camera data |
| F06-005 | Animer sensor shift | [ ] | - | - | - | Si POI bouge |
| F06-006 | FOV compensation calc | [ ] | - | - | - | Ratio math |
| F06-007 | Appliquer FOV adjusted | [ ] | - | - | - | camera.lens |
| F06-008 | Handheld Z oscillation | [ ] | - | - | - | Sin wave 1.8Hz |
| F06-009 | Handheld rotation noise | [ ] | - | - | - | XY random |
| F06-010 | Breathing cycle driver | [ ] | - | - | - | Subtle lens change |
| F06-011 | F-curves smoothing | [ ] | - | - | - | Bezier handles |
| F06-012 | Exporter scene_animated.blend | [ ] | - | - | - | Save file |
| F06-013 | Test Smart-Crop H→V | [ ] | - | - | - | Visual validation |
| F06-014 | Test Smart-Crop H→S | [ ] | - | - | - | Visual validation |
| F06-015 | Tests unitaires F06 | [ ] | - | - | - | Animation data |
| F06-016 | Documentation F06 | [ ] | - | - | - | Handheld params |

### F07 - ALCHIMISTE

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F07-001 | Configuration Cycles GPU | [ ] | - | - | - | CUDA setup |
| F07-002 | Samples par mode TURBO | [ ] | - | - | - | 16/32/128 |
| F07-003 | Denoiser setup | [ ] | - | - | - | OIDN vs OptiX |
| F07-004 | Resolution par mode | [ ] | - | - | - | Matrix lookup |
| F07-005 | Render single frame test | [ ] | - | - | - | Validation |
| F07-006 | Render animation batch | [ ] | - | - | - | bpy.ops.render |
| F07-007 | Export PNG 16-bit | [ ] | - | - | - | Color depth |
| F07-008 | Progress tracking | [ ] | - | - | - | Callbacks ou polling |
| F07-009 | Install Real-ESRGAN | [ ] | - | - | - | pip ou ncnn |
| F07-010 | Test ESRGAN single | [ ] | - | - | - | 540p→2160p |
| F07-011 | Batch ESRGAN | [ ] | - | - | - | Toutes frames |
| F07-012 | VRAM optimization ESRGAN | [ ] | - | - | - | Tile size |
| F07-013 | Install RIFE | [ ] | - | - | - | rife-ncnn-vulkan |
| F07-014 | Test RIFE single | [ ] | - | - | - | 24→60fps |
| F07-015 | Batch RIFE | [ ] | - | - | - | Interpolation |
| F07-016 | Chain ESRGAN→RIFE | [ ] | - | - | - | Mode CONQUÉRANT |
| F07-017 | Tests unitaires F07 | [ ] | - | - | - | Render validation |
| F07-018 | Documentation F07 | [ ] | - | - | - | Upscale pipeline |

---

## Phase 3: Industrialisation

### F08 - PORTE-AVIONS

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| F08-001 | FFmpeg encoding basic | [ ] | - | - | - | Frames→MP4 |
| F08-002 | Codec selection | [ ] | - | - | - | H.264 vs HEVC |
| F08-003 | CRF tuning | [ ] | - | - | - | Quality vs size |
| F08-004 | FPS paramétrable | [ ] | - | - | - | Per mode |
| F08-005 | Audio procedural design | [ ] | - | - | - | Architecture |
| F08-006 | Room tone generation | [ ] | - | - | - | Ambient layer |
| F08-007 | Footsteps synthesis | [ ] | - | - | - | Sync with Z |
| F08-008 | Breathing audio | [ ] | - | - | - | Subtle layer |
| F08-009 | Mix audio layers | [ ] | - | - | - | Level balance |
| F08-010 | Audio export | [ ] | - | - | - | AAC encoding |
| F08-011 | Mux video+audio | [ ] | - | - | - | FFmpeg -i |
| F08-012 | Noise injection color | [ ] | - | - | - | colorbalance |
| F08-013 | Noise injection grain | [ ] | - | - | - | noise filter |
| F08-014 | Speed variation | [ ] | - | - | - | setpts |
| F08-015 | Crop variation | [ ] | - | - | - | Micro pad/crop |
| F08-016 | Multi-format export | [ ] | - | - | - | YT, TikTok, IG |
| F08-017 | Variant generation | [ ] | - | - | - | N variantes |
| F08-018 | Batch processing | [ ] | - | - | - | Queue system |
| F08-019 | Tests unitaires F08 | [ ] | - | - | - | Video validation |
| F08-020 | Documentation F08 | [ ] | - | - | - | Export formats |

### P3 - Automation

| ID | Tâche | Status | Assigné | Date Début | Date Fin | Notes |
|----|-------|--------|---------|------------|----------|-------|
| P3-001 | YouTube API setup | [ ] | - | - | - | OAuth + credentials |
| P3-002 | Upload video function | [ ] | - | - | - | API call |
| P3-003 | Metadata generation | [ ] | - | - | - | Title, desc via Gemini |
| P3-004 | Thumbnail generation | [ ] | - | - | - | Frame extraction + text |
| P3-005 | Upload scheduler | [ ] | - | - | - | Cron ou manual trigger |
| P3-006 | Analytics tracking | [ ] | - | - | - | Views, engagement |
| P3-007 | TikTok integration | [ ] | - | - | - | API ou manual |
| P3-008 | Instagram integration | [ ] | - | - | - | API ou manual |

---

## Statistiques

### Compteurs

| Phase | Total | À faire | En cours | Complété | Bloqué |
|-------|-------|---------|----------|----------|--------|
| P0 | 16 | 13 | 1 | 2 | 0 |
| F01 | 22 | 22 | 0 | 0 | 0 |
| F02 | 17 | 17 | 0 | 0 | 0 |
| F03 | 15 | 3 | 0 | 12 | 0 |
| F04 | 17 | 17 | 0 | 0 | 0 |
| F05 | 15 | 15 | 0 | 0 | 0 |
| F06 | 16 | 16 | 0 | 0 | 0 |
| F07 | 18 | 18 | 0 | 0 | 0 |
| F08 | 20 | 20 | 0 | 0 | 0 |
| P3 | 8 | 8 | 0 | 0 | 0 |
| **TOTAL** | **164** | **149** | **1** | **14** | **0** |

### Progression Globale

```
[█████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 9%
```

---

## Notes de Mise à Jour

| Date | Auteur | Changements |
|------|--------|-------------|
| 2026-02-06 | Vulkan | Création initiale, structure complète |
| 2026-02-06 | Capy | F03-SCÉNOGRAPHE implémenté (12 tâches) |

---

*Dernière mise à jour: 2026-02-06*
