# SPECULUM_VALIDATION.md - Rituel d'Inquisition
> Protocoles de test EXODUS-SPECULUM

---

## 1. Tests Unitaires par Frégate

### F01-SCANNER Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T01-001 | Frame extraction | video.mp4 30sec | 60 PNG frames (2fps) | ±2 frames | ⬜ |
| T01-002 | Frame dimensions | 1080p source | 1920x1080 PNG | Exact | ⬜ |
| T01-003 | Depth map generation | 1080p frame | 16-bit PNG, same dims | 0 | ⬜ |
| T01-004 | Depth map range | Any frame | Values 0-65535 | - | ⬜ |
| T01-005 | Depth inference VRAM | Single frame | <6GB peak | +1GB | ⬜ |
| T01-006 | YOLO detection | Room image | JSON with ≥1 object | - | ⬜ |
| T01-007 | YOLO confidence | Detected objects | Confidence >0.5 | - | ⬜ |
| T01-008 | YOLO bbox format | Detection | [x1, y1, x2, y2] ints | - | ⬜ |
| T01-009 | SAM mask generation | YOLO bbox | Binary mask PNG | - | ⬜ |
| T01-010 | SAM mask dimensions | Frame 1080p | 1920x1080 mask | Exact | ⬜ |
| T01-011 | spatial_data.json schema | Full scan | Valid JSON schema | - | ⬜ |
| T01-012 | spatial_data completeness | Full scan | All frames indexed | - | ⬜ |

### F02-CORTEX Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T02-001 | Gemini API connection | API key | 200 response | - | ⬜ |
| T02-002 | Vision analysis | 3 keyframes | JSON response | - | ⬜ |
| T02-003 | Room type detection | Living room image | "living_room" string | - | ⬜ |
| T02-004 | Dimensions estimation | Standard room | 3-10m per dimension | ±50% | ⬜ |
| T02-005 | Materials detection | Room with hardwood | "hardwood" in materials | - | ⬜ |
| T02-006 | Furniture count | Room with 5 items | ≥3 items detected | - | ⬜ |
| T02-007 | masterplan.json schema | Full analysis | Valid JSON schema | - | ⬜ |
| T02-008 | POI heatmap generation | Keyframes | 32x32 float array | - | ⬜ |
| T02-009 | Rate limit handling | 70 rapid calls | Retry success | - | ⬜ |
| T02-010 | Cache hit | Repeated call | No API call | - | ⬜ |

### F03-SCÉNOGRAPHE Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T03-001 | Blender bpy import | import bpy | No error | - | ⬜ |
| T03-002 | Plane creation | Script | Plane object exists | - | ⬜ |
| T03-003 | Subdivision level | Plane | 4096+ faces | - | ⬜ |
| T03-004 | Displacement modifier | Plane + depth | Modifier active | - | ⬜ |
| T03-005 | Displacement effect | Render preview | Visible depth variation | Visual | ⬜ |
| T03-006 | Room shell complete | masterplan | 6 displaced planes | - | ⬜ |
| T03-007 | Proxy cube creation | Sofa in masterplan | Cube with dims | ±10% | ⬜ |
| T03-008 | Proxy cylinder creation | Lamp in masterplan | Cylinder exists | - | ⬜ |
| T03-009 | ghost_proxy tag | All proxies | Property set True | - | ⬜ |
| T03-010 | scene_shell.blend export | Script | File exists, <50MB | - | ⬜ |
| T03-011 | Collections structure | .blend file | ROOM_SHELL, PROXIES | - | ⬜ |

### F04-PROJECTIONNISTE Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T04-001 | Camera creation | Script | Camera object exists | - | ⬜ |
| T04-002 | UV Project single | 1 keyframe | UV layer created | - | ⬜ |
| T04-003 | UV Project multi | 3 keyframes | 3 UV layers | - | ⬜ |
| T04-004 | Texture node creation | Frame image | ShaderNodeTexImage | - | ⬜ |
| T04-005 | UV-Texture link | UV + Texture | Connected nodes | - | ⬜ |
| T04-006 | Mix shader setup | 3 textures | Mix nodes connected | - | ⬜ |
| T04-007 | Driver weight_frame0 | progress=0.0 | weight=1.0 | ±0.01 | ⬜ |
| T04-008 | Driver weight_frame0 | progress=0.5 | weight=0.0 | ±0.01 | ⬜ |
| T04-009 | Driver weight_frame50 | progress=0.5 | weight=1.0 | ±0.01 | ⬜ |
| T04-010 | Driver weight_frame100 | progress=1.0 | weight=1.0 | ±0.01 | ⬜ |
| T04-011 | Parallax drift test | 15° camera rotation | Pixel drift <5% | <2% target | ⬜ |
| T04-012 | Multi-projection blend | Animation midpoint | Smooth transition | Visual | ⬜ |
| T04-013 | Edge feathering | Border regions | No hard seams | Visual | ⬜ |
| T04-014 | scene_projected.blend | Script | File exists | - | ⬜ |

### F05-LOGISTIQUE Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T05-001 | Ghost proxy detection | scene_projected | List of proxies | - | ⬜ |
| T05-002 | Asset matching | Proxy "sofa" | Best match path | - | ⬜ |
| T05-003 | Dimension similarity | Proxy vs Asset | Score <0.3 | - | ⬜ |
| T05-004 | Linked asset load | Asset path | Object in scene | - | ⬜ |
| T05-005 | Asset positioning | Proxy location | Asset at same loc | ±0.01m | ⬜ |
| T05-006 | Proxy hiding | After replace | hide_render=True | - | ⬜ |
| T05-007 | LOD switching | Distance 1m | LOD0 active | - | ⬜ |
| T05-008 | LOD switching | Distance 5m | LOD1 active | - | ⬜ |
| T05-009 | No match fallback | Unknown type | Proxy kept visible | - | ⬜ |
| T05-010 | scene_furnished.blend | Script | File exists | - | ⬜ |

### F06-DIRECTEUR_PHOTO Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T06-001 | Ratio detection | 1920x1080 | "HORIZONTAL" | - | ⬜ |
| T06-002 | Ratio detection | 1080x1920 | "VERTICAL" | - | ⬜ |
| T06-003 | Sensor shift calc | POI at (0.7, 0.5) | shift_x ≈ 0.03 | ±0.01 | ⬜ |
| T06-004 | Sensor shift limit | POI at edge | shift ≤ 0.15 | - | ⬜ |
| T06-005 | FOV compensation | H→V conversion | FOV increased | 1.2-1.3x | ⬜ |
| T06-006 | Handheld Z amplitude | Animation | Range ±0.02m | ±0.005 | ⬜ |
| T06-007 | Handheld Z frequency | Animation | ~1.8Hz | ±0.2Hz | ⬜ |
| T06-008 | Rotation noise presence | Animation | Non-zero values | - | ⬜ |
| T06-009 | Rotation noise range | Animation | <0.01 rad | - | ⬜ |
| T06-010 | Breathing cycle | 4sec segment | Visible lens change | - | ⬜ |
| T06-011 | scene_animated.blend | Script | File exists | - | ⬜ |

### F07-ALCHIMISTE Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T07-001 | Cycles GPU active | Render | device='GPU' | - | ⬜ |
| T07-002 | Samples ÉCLAIREUR | Mode check | samples=16 | - | ⬜ |
| T07-003 | Samples CONQUÉRANT | Mode check | samples=32 | - | ⬜ |
| T07-004 | Samples SOUVERAIN | Mode check | samples=128 | - | ⬜ |
| T07-005 | Denoiser active | Render | use_denoising=True | - | ⬜ |
| T07-006 | Render single frame | Scene | PNG output exists | - | ⬜ |
| T07-007 | Render resolution | CONQUÉRANT | 960x540 | Exact | ⬜ |
| T07-008 | ESRGAN 4x upscale | 540p frame | 2160p output | Exact | ⬜ |
| T07-009 | ESRGAN VRAM | Single frame | <5GB peak | <6GB | ⬜ |
| T07-010 | RIFE interpolation | 2 frames | 5 frames output | - | ⬜ |
| T07-011 | RIFE quality | Interpolated | No visible ghosting | Visual | ⬜ |
| T07-012 | Chain ESRGAN→RIFE | 540p/24fps | 2160p/60fps | - | ⬜ |
| T07-013 | Total VRAM peak | Full render | <14GB | <16GB | ⬜ |

### F08-PORTE_AVIONS Tests

| ID | Test | Input | Expected Output | Tolérance | Status |
|----|------|-------|-----------------|-----------|--------|
| T08-001 | FFmpeg encoding | Frames dir | MP4 output | - | ⬜ |
| T08-002 | Output playable | MP4 file | VLC plays OK | - | ⬜ |
| T08-003 | Output FPS | CONQUÉRANT | 60fps | ±1fps | ⬜ |
| T08-004 | Output resolution | CONQUÉRANT | 3840x2160 | Exact | ⬜ |
| T08-005 | Audio generation | 30sec duration | AAC file | - | ⬜ |
| T08-006 | Audio sync | Video + audio | Aligned | ±100ms | ⬜ |
| T08-007 | Noise injection | Original video | Different hash | - | ⬜ |
| T08-008 | Noise imperceptible | Injected video | SSIM >0.99 | - | ⬜ |
| T08-009 | Multi-format YouTube | Master | 3840x2160 H.265 | - | ⬜ |
| T08-010 | Multi-format TikTok | Master | 1080x1920 H.264 | - | ⬜ |
| T08-011 | Variant uniqueness | 5 variants | 5 different hashes | - | ⬜ |
| T08-012 | Variant visual similarity | 5 variants | SSIM >0.95 | - | ⬜ |

---

## 2. Tests d'Intégration

### Pipeline End-to-End

| ID | Test | Description | Input | Pass Criteria | Status |
|----|------|-------------|-------|---------------|--------|
| INT-001 | ÉCLAIREUR E2E | Pipeline complet mode preview | 30sec 1080p video | 540p/12fps output, <30min | ⬜ |
| INT-002 | CONQUÉRANT E2E | Pipeline complet mode production | 30sec 1080p video | 4K/60fps output, <3h | ⬜ |
| INT-003 | SOUVERAIN E2E | Pipeline complet mode ultra | 30sec 1080p video | Native 4K/60fps, <8h | ⬜ |
| INT-004 | Format H→V | Smart crop horizontal to vertical | 16:9 source | 9:16 output, POI centered | ⬜ |
| INT-005 | Format H→S | Smart crop horizontal to square | 16:9 source | 1:1 output, no black bars | ⬜ |
| INT-006 | Multi-variant | Generate 5 variants | Master video | 5 unique outputs | ⬜ |
| INT-007 | Batch processing | 3 videos sequential | 3 sources | 3 outputs, no crash | ⬜ |

### Frégate Handoffs

| ID | Test | From | To | Validation |
|----|------|------|-----|------------|
| HO-001 | Scanner→Cortex | spatial_data.json | masterplan.json | Schema valid both |
| HO-002 | Cortex→Scénographe | masterplan.json | scene_shell.blend | Proxies match furniture |
| HO-003 | Scanner→Projectionniste | depth_maps/ | scene_projected.blend | Displacement applied |
| HO-004 | Scénographe→Projectionniste | scene_shell.blend | scene_projected.blend | All surfaces textured |
| HO-005 | Projectionniste→Logistique | scene_projected.blend | scene_furnished.blend | Assets loaded |
| HO-006 | Logistique→DirecteurPhoto | scene_furnished.blend | scene_animated.blend | Camera animated |
| HO-007 | DirecteurPhoto→Alchimiste | scene_animated.blend | frames/ | Correct resolution |
| HO-008 | Alchimiste→PorteAvions | frames/ | final_output.mp4 | Playable video |

---

## 3. Tests de Performance

### Benchmarks par Frégate

| ID | Test | Target | Acceptable | Measured | Status |
|----|------|--------|------------|----------|--------|
| PERF-001 | F01 Depth inference (single) | <2s | <4s | - | ⬜ |
| PERF-002 | F01 YOLO detection (single) | <0.5s | <1s | - | ⬜ |
| PERF-003 | F01 SAM segmentation (single) | <1s | <2s | - | ⬜ |
| PERF-004 | F01 Full scan (30sec video) | <10min | <15min | - | ⬜ |
| PERF-005 | F02 Gemini call | <5s | <10s | - | ⬜ |
| PERF-006 | F03 Scene generation | <30s | <60s | - | ⬜ |
| PERF-007 | F04 Projection setup | <60s | <120s | - | ⬜ |
| PERF-008 | F05 Asset loading | <30s | <60s | - | ⬜ |
| PERF-009 | F06 Animation setup | <20s | <40s | - | ⬜ |
| PERF-010 | F07 Render/frame ÉCLAIREUR | <0.5s | <1s | - | ⬜ |
| PERF-011 | F07 Render/frame CONQUÉRANT | <2s | <3s | - | ⬜ |
| PERF-012 | F07 Render/frame SOUVERAIN | <10s | <15s | - | ⬜ |
| PERF-013 | F07 ESRGAN upscale/frame | <1s | <2s | - | ⬜ |
| PERF-014 | F07 RIFE interpolation/pair | <0.5s | <1s | - | ⬜ |
| PERF-015 | F08 Encoding (30sec) | <60s | <120s | - | ⬜ |

### VRAM Usage

| ID | Test | Target | Acceptable | Measured | Status |
|----|------|--------|------------|----------|--------|
| VRAM-001 | Depth Anything V2 peak | <5GB | <6GB | - | ⬜ |
| VRAM-002 | YOLOv8x peak | <3GB | <4GB | - | ⬜ |
| VRAM-003 | SAM ViT-H peak | <4GB | <5GB | - | ⬜ |
| VRAM-004 | Blender Cycles peak | <8GB | <10GB | - | ⬜ |
| VRAM-005 | Real-ESRGAN peak | <5GB | <6GB | - | ⬜ |
| VRAM-006 | RIFE peak | <2GB | <3GB | - | ⬜ |
| VRAM-007 | Max concurrent (any 2) | <14GB | <16GB | - | ⬜ |

### Total Pipeline Time

| ID | Test | Mode | Target | Acceptable | Measured | Status |
|----|------|------|--------|------------|----------|--------|
| TIME-001 | 30sec video | ÉCLAIREUR | <30min | <45min | - | ⬜ |
| TIME-002 | 30sec video | CONQUÉRANT | <2h | <3h | - | ⬜ |
| TIME-003 | 30sec video | SOUVERAIN | <6h | <8h | - | ⬜ |
| TIME-004 | 60sec video | CONQUÉRANT | <3.5h | <5h | - | ⬜ |
| TIME-005 | Batch 5 videos | CONQUÉRANT | <10h | <15h | - | ⬜ |

---

## 4. Tests de Qualité Visuelle

### Métriques Objectives

| ID | Test | Metric | Target | Acceptable | Status |
|----|------|--------|--------|------------|--------|
| VQ-001 | Overall similarity | SSIM vs source | >0.92 | >0.85 | ⬜ |
| VQ-002 | Color accuracy | PSNR | >35dB | >30dB | ⬜ |
| VQ-003 | Parallax stability | Pixel drift @15° | <2% | <5% | ⬜ |
| VQ-004 | Upscale artifacts | NIQE score | <4.0 | <5.0 | ⬜ |
| VQ-005 | Temporal consistency | FlowNet error | <2px | <4px | ⬜ |
| VQ-006 | Interpolation quality | RIFE SSIM | >0.97 | >0.95 | ⬜ |

### Review Visuelle (Checklist)

| ID | Item | Critère | Status |
|----|------|---------|--------|
| VR-001 | Depth perception | Relief visible sur murs/sols | ⬜ |
| VR-002 | Texture clarity | Pas de blur excessif | ⬜ |
| VR-003 | Edge transitions | Pas de seams visibles | ⬜ |
| VR-004 | Parallax naturel | Mouvement 3D convaincant | ⬜ |
| VR-005 | Handheld feel | Mouvement organique | ⬜ |
| VR-006 | Color preservation | Tons fidèles à source | ⬜ |
| VR-007 | Upscale quality | Pas d'artefacts blocs | ⬜ |
| VR-008 | Interpolation smooth | Pas de ghosting | ⬜ |
| VR-009 | Audio sync | Son aligné avec mouvement | ⬜ |
| VR-010 | Overall polish | Qualité professionnelle | ⬜ |

---

## 5. Tests Anti-Shadowban

| ID | Test | Description | Pass Criteria | Status |
|----|------|-------------|---------------|--------|
| ASB-001 | Hash uniqueness | 2 variants same source | Different MD5 | ⬜ |
| ASB-002 | Perceptual hash diff | 2 variants | pHash differs | ⬜ |
| ASB-003 | Audio fingerprint diff | 2 variants | AudioFP differs | ⬜ |
| ASB-004 | Metadata variation | 2 variants | Different EXIF | ⬜ |
| ASB-005 | Visual similarity | 2 variants | SSIM >0.95 (similar) | ⬜ |
| ASB-006 | YouTube upload test | Variant | No duplicate warning | ⬜ |
| ASB-007 | TikTok upload test | Variant | No shadowban 24h | ⬜ |

---

## 6. Checklist Pré-Release

### Alpha Release (M1)
- [ ] Tous tests T01-* passent
- [ ] Tous tests T04-* passent
- [ ] INT-001 (ÉCLAIREUR E2E) passe
- [ ] VRAM peak <16GB

### Beta Release (M2)
- [ ] Tous tests unitaires passent
- [ ] INT-002 (CONQUÉRANT E2E) passe
- [ ] PERF-011 <3s
- [ ] VQ-001 SSIM >0.85

### Production Release (M3)
- [ ] Tous tests passent
- [ ] INT-006 (Multi-variant) passe
- [ ] TIME-002 <3h
- [ ] ASB-006, ASB-007 passent
- [ ] VR-010 "Qualité professionnelle" validé
- [ ] Documentation complète

---

## 7. Automation Tests

### CI/CD Triggers (Future)
```yaml
# .github/workflows/test.yml - À implémenter
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  unit_tests:
    # Run T01-T08 sans GPU
  integration_tests:
    # Run INT-* avec GPU (self-hosted ou Colab)
```

### Test Data Repository
```
test_data/
├── videos/
│   ├── living_room_30sec_1080p.mp4
│   ├── bedroom_30sec_1080p.mp4
│   └── kitchen_30sec_1080p.mp4
├── expected_outputs/
│   ├── depth_maps/
│   ├── masterplan_samples/
│   └── render_references/
└── golden_masters/
    └── reference_outputs/
```

---

## Notes de Version

| Date | Version | Changements |
|------|---------|-------------|
| 2026-02-06 | 0.1.0 | Création initiale, structure complète |

---

*Dernière mise à jour: 2026-02-06*
*Tests définis: 120+*
*Tests passés: 0*
