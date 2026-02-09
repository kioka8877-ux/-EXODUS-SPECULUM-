# SPECULUM_ROADMAP.md - Plan de Conquête
> Chronologie de développement EXODUS-SPECULUM

---

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXODUS-SPECULUM CONQUEST TIMELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 0          PHASE 1           PHASE 2          PHASE 3               │
│  FONDATIONS       PROOF OF          CORE             INDUSTRIALISATION     │
│                   CONCEPT           PIPELINE                                │
│                                                                             │
│  ████████░░░░     ░░░░░░░░░░░░     ░░░░░░░░░░░░     ░░░░░░░░░░░░          │
│                                                                             │
│  Semaine 1        Semaine 2-3       Semaine 4-6      Semaine 7-8           │
│                                                                             │
│  Docs +           Premier           8 Frégates       Multi-variant +       │
│  Setup            rendu test        complètes        Automation            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: FONDATIONS (Semaine 1)

**Objectif:** Établir la base documentaire et l'infrastructure.

### Tâches

| ID | Tâche | Status | Assigné | ETA |
|----|-------|--------|---------|-----|
| P0-001 | Créer Hexagramme documentaire | 🔄 En cours | Vulkan | J1 |
| P0-002 | Setup repository structure | ⬜ À faire | - | J1 |
| P0-003 | Configurer .gitignore | ⬜ À faire | - | J1 |
| P0-004 | Créer template Colab de base | ⬜ À faire | - | J2 |
| P0-005 | Script installation dépendances | ⬜ À faire | - | J2-3 |
| P0-006 | Setup Blender headless sur Colab | ⬜ À faire | - | J3-4 |
| P0-007 | Test Gemini API integration | ⬜ À faire | - | J4 |
| P0-008 | Structure ASSETSHUB | ⬜ À faire | - | J5 |

### Livrables Phase 0
- [x] Documentation complète (6 fichiers)
- [ ] Repository structuré
- [ ] Colab notebook fonctionnel (vide mais exécutable)
- [ ] Dépendances installables en <5min

### Critères de Validation
- Tous documents mergés dans main
- Colab exécute sans erreur (cells vides)
- Blender bpy importable sur Colab

---

## Phase 1: PROOF OF CONCEPT (Semaine 2-3)

**Objectif:** Premier rendu fonctionnel d'une pièce simple.

### Sprint 1.1: Scanner + Extraction (J8-11)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P1-001 | Intégration FFmpeg extraction | ⬜ | P0-004 |
| P1-002 | Intégration Depth Anything V2 | ⬜ | P0-005 |
| P1-003 | Test depth sur 10 images | ⬜ | P1-002 |
| P1-004 | Export depth_maps/ structure | ⬜ | P1-003 |

**Validation Sprint 1.1:**
- [ ] Depth maps générées pour vidéo test 30sec
- [ ] VRAM <10GB pendant inference
- [ ] Qualité depth visually acceptable

### Sprint 1.2: Projectionniste Basic (J12-17)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P1-005 | Créer script Blender projection basique | ⬜ | P0-006 |
| P1-006 | UV Project single frame | ⬜ | P1-005 |
| P1-007 | Ajouter displacement | ⬜ | P1-004, P1-006 |
| P1-008 | Render test 540p/12fps | ⬜ | P1-007 |
| P1-009 | Export MP4 via FFmpeg | ⬜ | P1-008 |

**Validation Sprint 1.2:**
- [ ] Vidéo 540p rendue (même avec artefacts)
- [ ] Displacement visible sur depth variations
- [ ] Pipeline end-to-end fonctionnel

### Livrables Phase 1
- [ ] Script F01-SCANNER v0.1
- [ ] Script F04-PROJECTIONNISTE v0.1
- [ ] Premier rendu vidéo (qualité preview)

### Milestone M1: Premier rendu 540p fonctionnel
**Critères:**
- Vidéo de sortie existe et est jouable
- Temps de pipeline <1h
- Pas de crash complet

---

## Phase 2: CORE PIPELINE (Semaine 4-6)

**Objectif:** Toutes les frégates opérationnelles en mode CONQUÉRANT.

### Sprint 2.1: Frégates 01-04 Complètes (J18-24)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P2-001 | F01: Ajouter YOLOv8 detection | ⬜ | M1 |
| P2-002 | F01: Ajouter SAM segmentation | ⬜ | P2-001 |
| P2-003 | F01: Export spatial_data.json | ⬜ | P2-002 |
| P2-004 | F02: Gemini integration | ⬜ | P0-007 |
| P2-005 | F02: Prompt engineering room analysis | ⬜ | P2-004 |
| P2-006 | F02: Export masterplan.json | ⬜ | P2-005 |
| P2-007 | F03: Blob geometry generation | ⬜ | P2-006 |
| P2-008 | F03: Proxy cubes/cylinders | ⬜ | P2-007 |
| P2-009 | F04: Multi-projection (3 keyframes) | ⬜ | P2-008 |
| P2-010 | F04: Blend drivers | ⬜ | P2-009 |

**Validation Sprint 2.1:**
- [ ] spatial_data.json généré avec objets détectés
- [ ] masterplan.json avec dimensions estimées
- [ ] Multi-projection blend visible

### Sprint 2.2: Frégates 05-06 (J25-31)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P2-011 | F05: Ghost Proxy system | ⬜ | P2-010 |
| P2-012 | F05: Asset matching algorithm | ⬜ | P2-011 |
| P2-013 | F05: Linked asset loading | ⬜ | P2-012 |
| P2-014 | F05: LOD system | ⬜ | P2-013 |
| P2-015 | F06: Sensor shift implementation | ⬜ | P2-014 |
| P2-016 | F06: Handheld F-curves | ⬜ | P2-015 |
| P2-017 | F06: FOV compensation | ⬜ | P2-016 |
| P2-018 | F06: Format conversion matrix | ⬜ | P2-017 |

**Validation Sprint 2.2:**
- [ ] Assets linkés remplacent proxies
- [ ] Handheld motion visible et naturelle
- [ ] Smart-Crop fonctionne H→V

### Sprint 2.3: Frégate 07 - Alchimiste (J32-38)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P2-019 | F07: Cycles render pipeline | ⬜ | P2-018 |
| P2-020 | F07: OptiX denoiser | ⬜ | P2-019 |
| P2-021 | F07: Real-ESRGAN integration | ⬜ | P2-020 |
| P2-022 | F07: RIFE integration | ⬜ | P2-021 |
| P2-023 | F07: Upscale chain automation | ⬜ | P2-022 |
| P2-024 | Test complet mode CONQUÉRANT | ⬜ | P2-023 |

**Validation Sprint 2.3:**
- [ ] 540p→4K upscaling fonctionne
- [ ] 24fps→60fps interpolation smooth
- [ ] VRAM <14GB pendant render

### Livrables Phase 2
- [ ] F01-F07 fonctionnelles
- [ ] Pipeline CONQUÉRANT complet
- [ ] Tests unitaires par frégate

### Milestone M2: Pipeline CONQUÉRANT complet
**Critères:**
- Video 4K/60fps générée
- Qualité visuelle acceptable (SSIM >0.85)
- Temps <3h pour vidéo 30sec

---

## Phase 2.5: CONTRACTS & VALIDATION

**Objectif:** Garantir qualité et limites de poids à chaque étape.

### Sous-Phase A: Output Contracts (CTR)
| ID | Tâche | Status | ETA |
|----|-------|--------|-----|
| CTR-001→006 | output_contracts.py complet | ⬜ | J1-2 |
| CTR-007→009 | Intégration F01/F06/F07 | ⬜ | J3 |

### Livrables Phase 2.5A
- [ ] CORE_CONFIG/output_contracts.py
- [ ] Validation intégrée dans pipelines critiques
- [ ] LOGBOOK mis à jour

---

## Phase 3: INDUSTRIALISATION (Semaine 7-8)

**Objectif:** Production automatisée multi-variant.

### Sprint 3.1: Frégate 08 + Audio (J39-45)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P3-001 | F08: FFmpeg encoding pipeline | ⬜ | M2 |
| P3-002 | F08: Audio procedural generation | ⬜ | P3-001 |
| P3-003 | F08: Footsteps sync | ⬜ | P3-002 |
| P3-004 | F08: Ambient room tone | ⬜ | P3-003 |
| P3-005 | F08: Noise injection | ⬜ | P3-004 |
| P3-006 | F08: Multi-format export | ⬜ | P3-005 |

### Sprint 3.2: Multi-Variant Generation (J46-52)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P3-007 | Système de variantes | ⬜ | P3-006 |
| P3-008 | Randomisation paramètres | ⬜ | P3-007 |
| P3-009 | Batch processing | ⬜ | P3-008 |
| P3-010 | Queue management | ⬜ | P3-009 |

### Sprint 3.3: YouTube Automation (J53-56)

| ID | Tâche | Status | Dépendances |
|----|-------|--------|-------------|
| P3-011 | YouTube API integration | ⬜ | P3-010 |
| P3-012 | Metadata generation (titre, desc) | ⬜ | P3-011 |
| P3-013 | Thumbnail generation | ⬜ | P3-012 |
| P3-014 | Upload scheduler | ⬜ | P3-013 |
| P3-015 | Analytics tracking | ⬜ | P3-014 |

### Livrables Phase 3
- [ ] F08 complète
- [ ] Système multi-variant (5+ variantes/source)
- [ ] Upload automation (optionnel)

### Milestone M3: 10 vidéos/jour automatisées
**Critères:**
- Batch de 10 vidéos en <20h
- Chaque variante unique (anti-shadowban)
- Upload automatique fonctionnel

---

## Dépendances Critiques

```
                    ┌─────────────────────────────────────────────┐
                    │           GRAPHE DE DÉPENDANCES             │
                    └─────────────────────────────────────────────┘

    ┌───────────┐                                    ┌───────────┐
    │    P0     │                                    │    P0     │
    │  Colab    │                                    │  Gemini   │
    │  Setup    │                                    │   API     │
    └─────┬─────┘                                    └─────┬─────┘
          │                                                │
          ▼                                                │
    ┌───────────┐         ┌───────────┐                   │
    │    F01    │         │    F01    │                   │
    │  FFmpeg   │────────►│  Depth    │                   │
    │           │         │  Anything │                   │
    └─────┬─────┘         └─────┬─────┘                   │
          │                     │                         │
          │    ┌────────────────┤                         │
          │    │                │                         │
          ▼    ▼                ▼                         ▼
    ┌───────────┐         ┌───────────┐           ┌───────────┐
    │    F01    │         │    F01    │           │    F02    │
    │  YOLOv8   │────────►│   SAM     │           │  CORTEX   │
    │           │         │           │           │           │
    └─────┬─────┘         └─────┬─────┘           └─────┬─────┘
          │                     │                       │
          └──────────┬──────────┘                       │
                     │                                  │
                     ▼                                  │
              ┌─────────────┐                           │
              │ spatial_data│◄──────────────────────────┘
              │    .json    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  masterplan │
              │    .json    │
              └──────┬──────┘
                     │
                     ▼
              ┌───────────┐
              │    F03    │
              │SCÉNOGRAPHE│
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    F04    │
              │PROJECTION │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    F05    │
              │LOGISTIQUE │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    F06    │
              │  CAMERA   │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    F07    │
              │ ALCHIMISTE│
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    F08    │
              │  OUTPUT   │
              └───────────┘
```

### Chemins Critiques

1. **Path Principal (le plus long):**
   ```
   P0 → F01-Depth → F03 → F04 → F05 → F06 → F07 → F08
   Durée estimée: 6 semaines
   ```

2. **Path IA (parallélisable):**
   ```
   P0-Gemini → F02-Cortex → (merge avec F03)
   Durée estimée: 2 semaines
   ```

3. **Path Detection (parallélisable):**
   ```
   F01-FFmpeg → F01-YOLO → F01-SAM → spatial_data.json
   Durée estimée: 1 semaine
   ```

---

## Jalons (Milestones)

### M1: Premier rendu 540p fonctionnel
- **Date cible:** Fin Semaine 3
- **Critères:**
  - [ ] Vidéo de sortie existe et jouable
  - [ ] Pipeline basic end-to-end
  - [ ] Temps <1h
- **Risques:** Blender setup complexity

### M2: Pipeline CONQUÉRANT complet
- **Date cible:** Fin Semaine 6
- **Critères:**
  - [ ] 4K/60fps output
  - [ ] SSIM >0.85 vs source
  - [ ] Temps <3h
  - [ ] VRAM <14GB
- **Risques:** ESRGAN/RIFE VRAM conflicts

### M3: 10 vidéos/jour automatisées
- **Date cible:** Fin Semaine 8
- **Critères:**
  - [ ] Batch 10 vidéos <20h
  - [ ] Anti-shadowban effective
  - [ ] Minimal human intervention
- **Risques:** Platform detection, rate limiting

---

## Métriques de Suivi

### Velocity Tracking

| Semaine | Tâches Planifiées | Tâches Complétées | Velocity |
|---------|-------------------|-------------------|----------|
| 1 | 8 | - | - |
| 2 | 4 | - | - |
| 3 | 5 | - | - |
| 4 | 10 | - | - |
| 5 | 8 | - | - |
| 6 | 6 | - | - |
| 7 | 6 | - | - |
| 8 | 5 | - | - |

### Burndown Chart (à mettre à jour)

```
Tâches restantes
     │
  52 ┤ ████████████████████████████████████████████████████
     │
  40 ┤
     │
  30 ┤
     │
  20 ┤
     │
  10 ┤
     │
   0 ┤─────────────────────────────────────────────────────►
     S1    S2    S3    S4    S5    S6    S7    S8   Semaine
```

---

## Ressources Requises

### Temps
- **Estimation totale:** 8 semaines (temps partiel)
- **Heures/semaine estimées:** 15-20h

### Compute
- **Google Colab Pro:** Recommandé mais pas obligatoire
- **GPU sessions:** ~100h total estimé

### Storage
- **Google Drive:** 50GB minimum pour assets
- **Colab temp:** 100GB pour processing

### APIs
- **Gemini:** Free tier (60 QPM)
- **YouTube API:** Free tier (si automation)

---

## Notes de Version

### v0.1.0 - 2026-02-06
- Création initiale du roadmap
- Structure phases définies
- Dépendances mappées

---

*Dernière mise à jour: 2026-02-06*
*Responsable: Vulkan, Maître de la Forge*
