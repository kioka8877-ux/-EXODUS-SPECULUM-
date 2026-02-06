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

### [2026-02-06] - F04-A: Frégate PROJECTIONNISTE - Camera Projection Mapping

**Contexte:**
Phase 1 Sprint F04-A - Implémentation de la Frégate PROJECTIONNISTE pour le Camera Projection Mapping. Projection des textures vidéo source sur la coquille 3D générée par F03-SCÉNOGRAPHE.

**Solution:**
- `camera_setup.py`: Configuration des 3 caméras de projection avec estimation de chemin
- `uv_projector.py`: Projection UV manuelle depuis la perspective caméra (headless compatible)
- `multi_projection_shader.py`: Matériau avec blending animé via drivers
- `projectionniste_pipeline.py`: Orchestration complète du pipeline F04

**Code critique:**
```python
# Projection UV depuis caméra (sans opérateur Blender)
def _project_uvs_from_camera_view(self, obj, camera, uv_name):
    cam_matrix = camera.matrix_world.inverted()
    for face in bm.faces:
        for loop in face.loops:
            world_co = obj.matrix_world @ loop.vert.co
            cam_co = cam_matrix @ world_co
            if cam_co.z >= 0:
                u, v = 0.5, 0.5  # Behind camera
            else:
                x_proj = cam_co.x / (-cam_co.z)
                y_proj = cam_co.y / (-cam_co.z)
                u = (x_proj / (fov_scale * aspect) + 1) / 2
                v = (y_proj / fov_scale + 1) / 2
            loop[uv_layer].uv = (u, v)

# Driver blending formulas
driver1.expression = "min(1, max(0, progress * 2))"      # mix1: frame0↔frame50
driver2.expression = "max(0, min(1, progress * 2 - 1))"  # mix2: result↔frame100
```

**Architecture implémentée:**
- `CameraSetup`: 9 types de mouvement supportés (linear_forward/backward, pan_left/right, orbit_cw/ccw, static, zoom_in/out)
- `UVProjector`: Projection manuelle compatible headless, 3 UV layers par surface
- `MultiProjectionShader`: Node tree complet (UV Map → Texture → Mix → Principled BSDF)
- Drivers sur `animation_progress` custom property (0.0 → 1.0)
- Collection `PROJECTION_CAMERAS` pour organisation

**Résultats:**
- 3 caméras de projection positionnées selon type mouvement masterplan
- 3 UV layers par surface (UV_Projection_0/1/2)
- Matériau `MultiProjection_Material` avec blending fonctionnel
- Métadonnées intégrées (exodus_version, keyframes_used, etc.)
- Compatible Blender 4.0+ headless (Colab)

**Leçon apprise:**
L'opérateur `bpy.ops.uv.project_from_view()` nécessite un contexte graphique. Pour le mode headless, implémenter la projection manuelle via matrices camera et calculs de perspective.

**Liens:**
- Commit: `🎥 F04-A: Frégate PROJECTIONNISTE - Camera Projection Mapping`

---

### [2026-02-06] - F03-A: Frégate SCÉNOGRAPHE - Génération Géométrie 3D

**Contexte:**
Phase 1 Sprint F03-A - Implémentation de la Frégate SCÉNOGRAPHE pour la génération de géométrie 3D via Blender Python (BPY). Création de la coquille architecturale "blob room" avec proxies Ghost.

**Solution:**
- `room_builder.py`: Génération des 6 surfaces (box room) avec subdivision et displacement
- `proxy_generator.py`: Création de proxies Ghost (cubes/cylindres) avec custom properties
- `opening_cutter.py`: Percement des ouvertures via Boolean Modifiers
- `scenographe_pipeline.py`: Orchestration complète du pipeline F03

**Code critique:**
```python
# Création surface avec displacement
def _create_surface(self, name, size, location, rotation):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    plane = bpy.context.active_object
    plane.name = f"{name}_Displaced"
    plane.scale = (size[0], size[1], 1)
    plane.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    subsurf = plane.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 0
    subsurf.render_levels = 6  # 512x512 faces
    subsurf.subdivision_type = 'SIMPLE'
    return plane

# Proxy avec ghost_proxy tag
obj["ghost_proxy"] = True
obj["proxy_type"] = furniture_type
obj["confidence"] = confidence_score
```

**Architecture implémentée:**
- `RoomBuilder`: 6 surfaces (Floor, Ceiling, 4 Walls) avec displacement modifier
- `ProxyGenerator`: Mapping type→primitive (25+ types supportés), matériau semi-transparent
- `OpeningCutter`: Boolean Difference pour fenêtres/portes/arches
- Collections organisées: `ROOM_SHELL` et `PROXIES`
- Métadonnées intégrées: `exodus_version`, `project_id`, `masterplan_source`

**Résultats:**
- 6 surfaces générées avec orientation correcte (normals vers intérieur)
- Proxies avec custom properties `ghost_proxy=True` pour F05-LOGISTIQUE
- Export `scene_shell.blend` avec collections organisées
- Compatible Blender 4.0+ headless (Colab)

**Leçon apprise:**
L'utilisation de `subdivision.render_levels` au lieu de `subdivision.levels` permet de garder le viewport léger tout en ayant un rendu haute résolution pour le displacement.

**Liens:**
- Commit: `🎭 F03-A: Frégate SCÉNOGRAPHE - Génération géométrie 3D`

---

### [2026-02-06] - F01-A: Frégate SCANNER - Extraction & Depth

**Contexte:** 
Phase 1 Sprint F01-A - Implémentation de la Frégate SCANNER pour extraction de frames et estimation de profondeur.

**Solution:**
- `frame_extractor.py`: Extraction via FFmpeg, support multi-format (MP4, MOV, AVI, MKV, WEBM)
- `depth_estimator.py`: Depth Anything V2 avec gestion VRAM T4
- `scanner_pipeline.py`: Orchestration complète des stages

**Code critique:**
```python
# Depth normalisé [0,1] → 16-bit PNG
depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)
depth_16bit = (depth * 65535).astype(np.uint16)
cv2.imwrite(output_path, depth_16bit)
```

**Optimisations VRAM:**
- Batch size = 1 pour ViT-Large (~4.5GB)
- `torch.cuda.empty_cache()` toutes les 50 frames
- Cleanup explicite après traitement
- Device detection automatique (CUDA/CPU)

**Résultats:** 
- Extraction frames: ~0.1s/frame
- Depth estimation ViT-Large: ~2s/frame (T4 GPU)
- VRAM usage: <6GB stable

**Leçon apprise:** 
Le modèle ViT-Large de Depth Anything V2 est optimal pour notre cas (qualité/VRAM). Ne pas utiliser Giant sur T4 (OOM).

**Liens:**
- Commit: `🔍 F01-A: Frégate SCANNER - Extraction frames & Depth Anything V2`

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
- [2026-02-06] F01-A: Depth Anything V2 integration

### Camera Projection
- [2026-02-06] F04-A: Frégate PROJECTIONNISTE - Camera Projection Mapping

### Blender Scripting
- [2026-02-06] F03-A: Frégate SCÉNOGRAPHE - Génération géométrie 3D
- [2026-02-06] F04-A: Frégate PROJECTIONNISTE - UV Projection & Shaders

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
| - | - | - | - |

---

## Snippets Réutilisables

### Blender Headless Setup (Colab)
```python
# À documenter après implémentation
```

### Depth Anything V2 Inference
```python
from depth_anything_v2.dpt import DepthAnythingV2

# Config ViT-Large
model = DepthAnythingV2(encoder='vitl', features=256, out_channels=[256, 512, 1024, 1024])
model.load_state_dict(torch.load('depth_anything_v2_vitl.pth'))
model.to('cuda').eval()

# Inference
with torch.no_grad():
    depth = model.infer_image(rgb_image)  # Returns normalized depth
```

### Gemini Vision API Call
```python
# À documenter après implémentation
```

### FFmpeg Frame Extraction
```bash
# Extraction à 2 fps en PNG lossless
ffmpeg -y -i input.mp4 -vf fps=2.0 -pix_fmt rgb24 frame_%04d.png
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
*Entrées: 4*
