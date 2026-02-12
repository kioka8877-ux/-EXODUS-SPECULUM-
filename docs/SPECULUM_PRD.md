# SPECULUM_PRD.md - Product Requirements Document
> Spécifications fonctionnelles EXODUS-SPECULUM v3.1

---

## 1. Vue d'Ensemble

### 1.1 Mission

**EXODUS-SPECULUM** transforme des vidéos immobilières réelles en clones 3D 4K/60FPS ultra-réalistes via Camera Projection Mapping.

**Objectif industriel:** Production automatisée de vidéos immobilières multi-format pour YouTube/TikTok à partir d'une seule source vidéo.

**Proposition de valeur:**
- 1 vidéo source → N variantes (angles, formats, styles)
- Qualité cinématographique sans équipement professionnel
- Pipeline 100% gratuit (Google Colab + outils open source)

### 1.2 Contraintes Absolues

| Contrainte | Valeur | Justification |
|------------|--------|---------------|
| Budget | 0€ | Outils gratuits uniquement |
| Hardware | Google Colab T4 | 16GB VRAM max |
| API Costs | Free tier only | Gemini 2.5 Flash 250 RPD, 10 RPM |
| Runtime | <3h/video (CONQUÉRANT) | Colab timeout |
| Output Quality | ≥1080p/24fps minimum | Platform requirements |

### 1.3 Stack Technologique

```
┌─────────────────────────────────────────────────────────────────┐
│                      STACK EXODUS-SPECULUM                      │
├─────────────────────────────────────────────────────────────────┤
│ COMPUTE      │ Google Colab Pro (T4 GPU, 16GB VRAM)            │
├──────────────┼──────────────────────────────────────────────────┤
│ DEPTH        │ Depth Anything V2 (ViT-Large, 335M params)      │
├──────────────┼──────────────────────────────────────────────────┤
│ DETECTION    │ YOLOv8x (68.7M params)                          │
├──────────────┼──────────────────────────────────────────────────┤
│ SEGMENTATION │ Segment Anything Model (SAM)                     │
├──────────────┼──────────────────────────────────────────────────┤
│ AI VISION    │ Gemini 2.5 Flash (via google-generativeai)       │
├──────────────┼──────────────────────────────────────────────────┤
│ 3D ENGINE    │ Blender 4.0+ (bpy headless)                     │
├──────────────┼──────────────────────────────────────────────────┤
│ UPSCALING    │ Real-ESRGAN 4x                                  │
├──────────────┼──────────────────────────────────────────────────┤
│ INTERPOLATION│ RIFE (via rife-ncnn-vulkan)                     │
├──────────────┼──────────────────────────────────────────────────┤
│ VIDEO        │ FFmpeg (H.264/HEVC encoding)                    │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## 2. Protocole TURBO-SPECULUM (Tri-Vitesse)

### 2.1 Mode ÉCLAIREUR (Preview)

**Objectif:** Validation rapide du pipeline, preview client

| Paramètre | Valeur |
|-----------|--------|
| Résolution render | 960×540 (540p) |
| Samples Cycles | 16 |
| FPS output | 12 |
| Denoiser | OpenImageDenoise |
| Upscaling | None |
| Temps estimé | <30 min |

**Use cases:**
- Test de nouveau contenu
- Preview pour validation client
- Debug pipeline

### 2.2 Mode CONQUÉRANT (Production)

**Objectif:** Production standard, équilibre qualité/temps

| Paramètre | Valeur |
|-----------|--------|
| Résolution render | 960×540 (internal) |
| Samples Cycles | 32 |
| FPS internal | 24 |
| Denoiser | OptiX |
| Upscale chain | ESRGAN 4x → RIFE 2.5x |
| Résolution finale | 3840×2160 (4K) |
| FPS final | 60 |
| Temps estimé | <2h |

**Pipeline upscaling:**
```
540p/24fps ──[ESRGAN 4x]──► 2160p/24fps ──[RIFE 2.5x]──► 2160p/60fps
```

**Use cases:**
- Production YouTube standard
- Batch processing
- Multi-variant generation

### 2.3 Mode SOUVERAIN (Ultra Quality)

**Objectif:** Qualité maximale, showcase/premium

| Paramètre | Valeur |
|-----------|--------|
| Résolution render | 3840×2160 (native 4K) |
| Samples Cycles | 128 |
| FPS output | 60 (native) |
| Denoiser | OptiX |
| Upscaling | None (native) |
| Temps estimé | <8h |

**Use cases:**
- Showcase portfolio
- Premium client delivery
- Référence qualité

---

## 3. Protocole FORMAT-ADAPT

### 3.1 Détection Ratio Automatique

```python
def detect_source_ratio(video_path):
    """Détecte le ratio de la vidéo source."""
    width, height = get_video_dimensions(video_path)
    ratio = width / height
    
    if ratio > 1.5:
        return "HORIZONTAL"  # 16:9 ou plus large
    elif ratio < 0.7:
        return "VERTICAL"    # 9:16 ou plus étroit
    else:
        return "SQUARE"      # ~1:1
```

### 3.2 Sélecteur de Destination

| Plateforme | Format Requis | Ratio | Résolution Cible |
|------------|---------------|-------|------------------|
| YouTube | HORIZONTAL | 16:9 | 3840×2160 |
| YouTube Shorts | VERTICAL | 9:16 | 2160×3840 |
| TikTok | VERTICAL | 9:16 | 1080×1920 |
| Instagram Reels | VERTICAL | 9:16 | 1080×1920 |
| Instagram Feed | SQUARE | 1:1 | 1080×1080 |

### 3.3 Smart-Crop (Sensor Shift + POI)

Quand le format source ≠ format destination, Smart-Crop optimise le recadrage.

**Principe:**
1. Identifier les POI (Points of Interest) via F02-CORTEX
2. Appliquer Sensor Shift dans Blender pour recentrer sans déformer
3. Ajuster FOV si nécessaire pour éviter les bords noirs

**Sensor Shift:**
```python
# Blender camera sensor shift
camera.data.shift_x = poi_offset_x * MAX_SENSOR_SHIFT  # ±0.15
camera.data.shift_y = poi_offset_y * MAX_SENSOR_SHIFT
```

**Avantages vs crop classique:**
- Pas de perte de résolution
- Perspective préservée
- Mouvement fluide du POI

### 3.4 Mathématiques FOV

**Compensation FOV lors de conversion format:**

```python
def calculate_fov_compensation(source_ratio, target_ratio, base_fov=50):
    """
    Calcule le FOV ajusté pour maintenir le contenu visible.
    
    Args:
        source_ratio: Ratio source (ex: 1.78 pour 16:9)
        target_ratio: Ratio cible (ex: 0.56 pour 9:16)
        base_fov: FOV horizontal de base en degrés
    
    Returns:
        adjusted_fov: FOV ajusté
    """
    if target_ratio < source_ratio:
        # Vertical crop: on perd sur les côtés
        # Augmenter FOV pour compenser (zoom out)
        crop_factor = target_ratio / source_ratio
        zoom_compensation = min(1 / crop_factor, MAX_ZOOM_FACTOR)
        adjusted_fov = base_fov * zoom_compensation
    else:
        # Horizontal crop: on perd en haut/bas
        adjusted_fov = base_fov
    
    return min(adjusted_fov, 120)  # Cap à 120° pour éviter distorsion
```

**Matrice de conversion:**

| Source → Target | Action | FOV Adjust |
|-----------------|--------|------------|
| HORIZONTAL → HORIZONTAL | None | 1.0x |
| HORIZONTAL → VERTICAL | Sensor shift + Zoom | 1.2-1.3x |
| HORIZONTAL → SQUARE | Sensor shift | 1.0-1.1x |
| VERTICAL → HORIZONTAL | Pillarbox ou Sensor shift | 0.8x |
| VERTICAL → VERTICAL | None | 1.0x |
| VERTICAL → SQUARE | Crop top/bottom | 1.0x |

---

## 4. Spécifications par Frégate

### 4.1 F01-SCANNER (Extraction)

**Mission:** Extraire toutes les données spatiales de la vidéo source.

**Input:**
```
video.mp4 (any resolution, any format)
```

**Traitement:**

1. **Frame Extraction (FFmpeg)**
   ```bash
   ffmpeg -i input.mp4 -vf "fps=2" frames/frame_%04d.png
   ```
   - 2 FPS pour analyse (économie VRAM)
   - Keyframes supplémentaires si motion détectée

2. **Depth Estimation (Depth Anything V2)**
   ```python
   from depth_anything_v2 import DepthAnythingV2
   model = DepthAnythingV2(encoder='vitl')
   depth_map = model.infer_image(frame)  # Returns 16-bit depth
   ```
   - Modèle: ViT-Large (335M params)
   - Output: PNG 16-bit, même dimensions que source

3. **Object Detection (YOLOv8)**
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8x.pt')
   results = model(frame)
   # Extract: class, bbox, confidence
   ```
   - Classes pertinentes: furniture, person, door, window, plant

4. **Segmentation (SAM)**
   ```python
   from segment_anything import sam_model_registry, SamPredictor
   sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth")
   predictor = SamPredictor(sam)
   masks = predictor.predict(point_coords=yolo_centers)
   ```
   - Masks binaires pour chaque objet détecté

**Output:**
```
scanner_output/
├── frames/
│   ├── frame_0001.png
│   ├── frame_0002.png
│   └── ...
├── depth_maps/
│   ├── depth_0001.png (16-bit)
│   └── ...
├── masks/
│   ├── mask_0001_obj001.png
│   └── ...
└── spatial_data.json
```

**Schema spatial_data.json:**
```json
{
  "video_info": {
    "resolution": [1920, 1080],
    "fps": 30,
    "duration_sec": 45,
    "frame_count": 90
  },
  "frames": [
    {
      "frame_id": 1,
      "timestamp_sec": 0.0,
      "objects": [
        {
          "id": "obj_001",
          "class": "couch",
          "confidence": 0.94,
          "bbox": [120, 340, 580, 620],
          "mask_path": "masks/mask_0001_obj001.png",
          "depth_median": 2.3
        }
      ]
    }
  ]
}
```

---

### 4.2 F02-CORTEX (Intelligence IA)

**Mission:** Analyser la scène et générer le masterplan architectural.

**Input:**
```
frames/ (keyframes sélectionnés)
spatial_data.json
```

**Traitement:**

1. **Sélection Keyframes**
   - Frame 0 (entrée)
   - Frame 50% (milieu)
   - Frame 100% (fin)
   - Frames avec rotation >15°

2. **Analyse Gemini 2.5 Flash (Single-Call Multi-Image)**
   Optimisé single-call: 3 keyframes + POI en 1 requête.
   ```python
   import google.generativeai as genai
   
   genai.configure(api_key=GEMINI_API_KEY)
   model = genai.GenerativeModel('gemini-2.5-flash')
   
   prompt = """
   Analyze this real estate video frames and provide:
   1. Room dimensions estimation (meters)
   2. Materials detected (floor, walls, ceiling)
   3. Furniture list with estimated positions
   4. Lighting mood (warm/cold/neutral)
   5. Points of interest for camera focus
   
   Output as JSON.
   """
   
   response = model.generate_content([prompt, frame1, frame2, frame3])
   ```

3. **POI Heatmap Generation**
   - Pondération: meubles statement > fenêtres > art > autres
   - Lissage temporel pour tracking fluide

**Output:**
```json
{
  "masterplan": {
    "room_type": "living_room",
    "dimensions_estimate": {
      "width_m": 6.5,
      "depth_m": 8.2,
      "height_m": 2.8
    },
    "materials": {
      "floor": "hardwood_oak",
      "walls": "white_matte_paint",
      "ceiling": "white_smooth"
    },
    "furniture": [
      {
        "type": "sofa",
        "subtype": "L-shaped_sectional",
        "position_normalized": [0.3, 0.6],
        "dimensions_estimate": [2.8, 1.5, 0.85],
        "color": "grey_fabric",
        "confidence": 0.89
      }
    ],
    "lighting": {
      "mood": "warm",
      "natural_sources": ["window_large_south"],
      "artificial_sources": ["ceiling_spots", "floor_lamp"]
    },
    "poi_heatmap": {
      "resolution": [32, 32],
      "data": [[0.1, 0.2, ...], ...]
    }
  }
}
```

---

### 4.3 F03-SCÉNOGRAPHE (Génération Géométrie)

**Mission:** Créer la géométrie 3D "blob" dans Blender.

**Input:**
```
masterplan.json
depth_maps/
```

**Traitement:**

1. **Création Plans Subdivisés**
   ```python
   import bpy
   
   # Créer plan pour chaque surface
   bpy.ops.mesh.primitive_plane_add(size=10)
   plane = bpy.context.active_object
   
   # Subdivision pour displacement
   bpy.ops.object.modifier_add(type='SUBSURF')
   plane.modifiers["Subdivision"].levels = 6  # 512x512 faces
   ```

2. **Displacement Modifier**
   ```python
   # Ajouter displacement
   bpy.ops.object.modifier_add(type='DISPLACE')
   displace = plane.modifiers["Displace"]
   displace.texture = depth_texture
   displace.strength = DISPLACEMENT_STRENGTH  # 0.5
   displace.mid_level = DISPLACEMENT_MIDLEVEL  # 0.5
   ```

3. **Proxy Geometry**
   ```python
   # Pour chaque meuble dans masterplan
   for furniture in masterplan['furniture']:
       if furniture['type'] in PROXY_SHAPES:
           create_proxy(furniture)
   
   def create_proxy(furniture):
       dims = furniture['dimensions_estimate']
       pos = furniture['position_normalized']
       
       if furniture['type'] in ['sofa', 'bed', 'table']:
           bpy.ops.mesh.primitive_cube_add()
       elif furniture['type'] in ['lamp', 'vase', 'plant']:
           bpy.ops.mesh.primitive_cylinder_add()
       
       obj = bpy.context.active_object
       obj.scale = dims
       obj.location = world_position(pos)
       obj['ghost_proxy'] = True  # Tag pour F05
       obj['proxy_type'] = furniture['type']
   ```

**Output:**
```
scene_shell.blend
├── Collection "ROOM_SHELL"
│   ├── Floor_Displaced
│   ├── Wall_North_Displaced
│   ├── Wall_South_Displaced
│   ├── Wall_East_Displaced
│   ├── Wall_West_Displaced
│   └── Ceiling_Displaced
├── Collection "PROXIES"
│   ├── Proxy_Sofa (ghost_proxy=True)
│   ├── Proxy_Table (ghost_proxy=True)
│   └── ...
└── Metadata
    └── masterplan_reference.json
```

---

### 4.4 F04-PROJECTIONNISTE (Camera Projection Mapping)

**Mission:** Projeter les textures source sur la géométrie 3D.

**Input:**
```
scene_shell.blend
frames/ (3 keyframes: 0%, 50%, 100%)
```

**Traitement:**

1. **UV Project from View**
   ```python
   # Pour chaque keyframe
   for i, frame_path in enumerate(keyframes):
       # Positionner caméra selon tracking estimé
       camera.location = estimated_positions[i]
       camera.rotation_euler = estimated_rotations[i]
       
       # Créer UV map
       bpy.ops.object.mode_set(mode='EDIT')
       bpy.ops.mesh.select_all(action='SELECT')
       bpy.ops.uv.project_from_view(camera_bounds=True)
       
       # Nommer UV map
       mesh.uv_layers.active.name = f"UV_Projection_{i}"
   ```

2. **Multi-Projection Shader**
   ```python
   # Node tree pour blending
   material = bpy.data.materials.new(name="MultiProjection")
   material.use_nodes = True
   nodes = material.node_tree.nodes
   links = material.node_tree.links
   
   # Créer texture nodes pour chaque projection
   for i in range(3):
       tex_node = nodes.new('ShaderNodeTexImage')
       tex_node.image = bpy.data.images.load(keyframes[i])
       
       uv_node = nodes.new('ShaderNodeUVMap')
       uv_node.uv_map = f"UV_Projection_{i}"
       
       links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])
   
   # Mix shaders avec drivers
   # weight_frame0 = max(0, 1 - camera_progress * 2)
   # weight_frame50 = 1 - abs(camera_progress - 0.5) * 2
   # weight_frame100 = max(0, camera_progress * 2 - 1)
   ```

3. **Blend Drivers**
   ```python
   # Ajouter driver pour camera_progress
   driver = mix_node.inputs['Fac'].driver_add('default_value')
   driver.driver.expression = "max(0, 1 - camera_progress * 2)"
   
   var = driver.driver.variables.new()
   var.name = "camera_progress"
   var.type = 'SINGLE_PROP'
   var.targets[0].id = camera
   var.targets[0].data_path = '["animation_progress"]'
   ```

4. **Edge Feathering**
   - Gradient falloff sur les bords pour éviter les seams visibles
   - Blend radius: 5% de la dimension de projection

**Output:**
```
scene_projected.blend
├── Materials
│   └── MultiProjection_Material
│       ├── UV_Projection_0 → frame_0001.png
│       ├── UV_Projection_1 → frame_0050.png
│       └── UV_Projection_2 → frame_0100.png
├── Drivers
│   └── camera_progress (0.0 → 1.0)
└── Projection_Cameras (reference)
```

---

### 4.5 F05-LOGISTIQUE (Asset Replacement)

**Mission:** Remplacer les Ghost Proxies par de vrais assets 3D.

**Input:**
```
scene_projected.blend
ASSETSHUB_PATH (bibliothèque d'assets)
```

**Traitement:**

1. **Ghost Proxy Detection**
   ```python
   ghost_proxies = [obj for obj in bpy.data.objects 
                    if obj.get('ghost_proxy') == True]
   ```

2. **Asset Matching**
   ```python
   def find_best_asset(proxy):
       proxy_type = proxy['proxy_type']
       proxy_dims = proxy.dimensions
       
       # Chercher dans ASSETSHUB
       candidates = glob(f"{ASSETSHUB_PATH}/{proxy_type}/*.blend")
       
       # Score par similarité de dimensions
       best_match = min(candidates, 
                        key=lambda x: dimension_diff(x, proxy_dims))
       return best_match
   ```

3. **Linked Asset Loading**
   ```python
   def replace_proxy(proxy, asset_path):
       # Link asset (pas append, pour économiser mémoire)
       with bpy.data.libraries.load(asset_path, link=True) as (data_from, data_to):
           data_to.objects = [name for name in data_from.objects 
                             if "LOD0" in name]
       
       # Positionner
       asset = data_to.objects[0]
       asset.location = proxy.location
       asset.rotation_euler = proxy.rotation_euler
       asset.scale = proxy.scale
       
       # Cacher proxy
       proxy.hide_render = True
       proxy.hide_viewport = True
   ```

4. **LOD System**
   - LOD0: Full detail (camera distance <2m)
   - LOD1: Medium (2-5m)
   - LOD2: Low (>5m)
   
   ```python
   # Driver pour LOD switching
   driver = obj.modifiers['Decimate'].driver_add('ratio')
   driver.driver.expression = "lod_factor(camera_distance)"
   ```

**Output:**
```
scene_furnished.blend
├── Collection "ASSETS_LINKED"
│   ├── Sofa_ModernGrey (linked from ASSETSHUB)
│   ├── Table_Oak (linked)
│   └── ...
├── Collection "PROXIES" (hidden)
└── LOD_Drivers
```

---

### 4.6 F06-DIRECTEUR_PHOTO (Camera Animation)

**Mission:** Animer la caméra avec effets handheld et Smart-Crop.

**Input:**
```
scene_furnished.blend
format_config (OUTPUT_FORMAT)
poi_heatmap (from masterplan)
```

**Traitement:**

1. **Sensor Shift pour Smart-Crop**
   ```python
   def apply_smart_crop(camera, source_format, target_format, poi_heatmap):
       if source_format == target_format:
           return
       
       # Calculer offset POI
       poi_center = calculate_poi_center(poi_heatmap)
       frame_center = (0.5, 0.5)
       offset = (poi_center[0] - frame_center[0], 
                 poi_center[1] - frame_center[1])
       
       # Appliquer sensor shift
       camera.data.shift_x = offset[0] * MAX_SENSOR_SHIFT
       camera.data.shift_y = offset[1] * MAX_SENSOR_SHIFT
       
       # Animer le shift si POI bouge
       if poi_moves:
           animate_sensor_shift(camera, poi_heatmap)
   ```

2. **Handheld F-Curves**
   ```python
   def add_handheld_motion(camera, duration_frames):
       # Z oscillation (walking bounce)
       z_fcurve = camera.animation_data.action.fcurves.new(
           data_path='location', index=2)
       
       for frame in range(duration_frames):
           t = frame / fps
           z_value = HANDHELD_Z_AMPLITUDE * math.sin(2 * math.pi * HANDHELD_Z_FREQ * t)
           z_fcurve.keyframe_points.insert(frame, z_value)
       
       # Rotation noise (micro-tremblements)
       for axis in [0, 1]:  # X et Y rotation
           rot_fcurve = camera.animation_data.action.fcurves.new(
               data_path='rotation_euler', index=axis)
           
           for frame in range(duration_frames):
               noise_value = random.gauss(0, HANDHELD_ROT_NOISE)
               rot_fcurve.keyframe_points.insert(frame, noise_value)
       
       # Breathing cycle (subtle zoom)
       breathing_driver = camera.data.driver_add('lens')
       breathing_driver.driver.expression = f"50 + 2 * sin(frame / {fps} * 2 * pi / {HANDHELD_BREATHING_CYCLE})"
   ```

3. **FOV Compensation**
   ```python
   def compensate_fov(camera, source_ratio, target_ratio):
       if target_ratio < source_ratio:
           crop_factor = target_ratio / source_ratio
           zoom_compensation = min(1 / crop_factor, MAX_ZOOM_FACTOR)
           camera.data.lens = camera.data.lens / zoom_compensation
   ```

**Output:**
```
scene_animated.blend
├── Camera
│   ├── Animation (handheld motion)
│   ├── Sensor Shift (smart crop)
│   └── FOV Compensation
└── Render Settings
    └── Resolution (per OUTPUT_FORMAT)
```

---

### 4.7 F07-ALCHIMISTE (Rendu + Upscaling)

**Mission:** Render Cycles + pipeline upscaling IA.

**Input:**
```
scene_animated.blend
TURBO_MODE
```

**Traitement:**

1. **Cycles Configuration**
   ```python
   def configure_cycles(mode):
       scene = bpy.context.scene
       scene.render.engine = 'CYCLES'
       scene.cycles.device = 'GPU'
       scene.cycles.samples = RENDER_PROFILES[mode]['samples']
       
       # Denoiser
       scene.cycles.use_denoising = True
       scene.cycles.denoiser = RENDER_PROFILES[mode]['denoiser']
       
       # Resolution
       res = RESOLUTION_MATRIX[mode][OUTPUT_FORMAT]
       scene.render.resolution_x = res[0]
       scene.render.resolution_y = res[1]
       
       # FPS
       scene.render.fps = RENDER_PROFILES[mode]['fps']
   ```

2. **Render Frames**
   ```python
   def render_animation(output_dir):
       scene.render.filepath = f"{output_dir}/frame_"
       scene.render.image_settings.file_format = 'PNG'
       scene.render.image_settings.color_depth = '16'
       
       bpy.ops.render.render(animation=True)
   ```

3. **Upscaling Chain (Mode CONQUÉRANT)**
   ```python
   def upscale_chain(frames_dir, mode):
       if mode != "conquerant":
           return
       
       # Step 1: Real-ESRGAN 4x
       subprocess.run([
           "realesrgan-ncnn-vulkan",
           "-i", frames_dir,
           "-o", f"{frames_dir}_4x",
           "-n", "realesrgan-x4plus",
           "-s", "4"
       ])
       
       # Step 2: RIFE 2.5x interpolation
       subprocess.run([
           "rife-ncnn-vulkan",
           "-i", f"{frames_dir}_4x",
           "-o", f"{frames_dir}_final",
           "-m", "rife-v4",
           "-x"  # 2.5x interpolation
       ])
   ```

**Output:**
```
render_output/
├── frames_raw/        # 540p si CONQUÉRANT
│   └── frame_0001.png ...
├── frames_4x/         # 2160p après ESRGAN
│   └── frame_0001.png ...
└── frames_final/      # 2160p/60fps après RIFE
    └── frame_0001.png ...
```

---

### 4.8 F08-PORTE_AVIONS (Assemblage Final)

**Mission:** Encoder la vidéo finale avec audio.

**Input:**
```
frames_final/ (ou frames_raw si ÉCLAIREUR/SOUVERAIN)
audio_config
```

**Traitement:**

1. **FFmpeg Encoding**
   ```python
   def encode_video(frames_dir, output_path, mode):
       fps = RENDER_PROFILES[mode]['fps']
       if mode == "conquerant":
           fps = 60  # Après RIFE
       
       # H.264 pour compatibilité, HEVC pour qualité
       codec = "libx264" if mode == "eclaireur" else "libx265"
       
       cmd = [
           "ffmpeg",
           "-framerate", str(fps),
           "-i", f"{frames_dir}/frame_%04d.png",
           "-c:v", codec,
           "-preset", "slow",
           "-crf", "18",
           "-pix_fmt", "yuv420p",
           output_path
       ]
       subprocess.run(cmd)
   ```

2. **Audio Procedural**
   ```python
   def generate_audio(duration_sec, output_path):
       # Layers audio:
       # 1. Ambient room tone
       # 2. Footsteps (synced with camera Z motion)
       # 3. Subtle breathing
       # 4. Occasional environment sounds
       
       ambient = generate_room_tone(duration_sec)
       footsteps = generate_footsteps(duration_sec, camera_z_keyframes)
       breathing = generate_breathing(duration_sec)
       
       # Mix
       final_audio = mix_layers([
           (ambient, 0.3),
           (footsteps, 0.5),
           (breathing, 0.2)
       ])
       
       export_audio(final_audio, output_path)
   ```

3. **Noise Injection Anti-Fingerprint**
   ```python
   def inject_noise(video_path, output_path):
       """
       Ajoute des variations imperceptibles pour éviter
       la détection de contenu dupliqué par les plateformes.
       """
       variations = [
           # Micro color shift
           f"colorbalance=rs=0.0{random.randint(1,9)}",
           # Subtle noise
           f"noise=alls={random.randint(1,3)}:allf=t",
           # Tiny speed variation
           f"setpts={1 + random.uniform(-0.001, 0.001)}*PTS"
       ]
       
       filter_chain = ",".join(variations)
       
       subprocess.run([
           "ffmpeg",
           "-i", video_path,
           "-vf", filter_chain,
           "-c:a", "copy",
           output_path
       ])
   ```

4. **Multi-Format Export**
   ```python
   def export_all_formats(master_video, output_dir):
       formats = {
           "youtube": {"resolution": "3840x2160", "bitrate": "45M"},
           "tiktok": {"resolution": "1080x1920", "bitrate": "10M"},
           "instagram": {"resolution": "1080x1080", "bitrate": "8M"}
       }
       
       for platform, settings in formats.items():
           output = f"{output_dir}/{platform}_export.mp4"
           # Apply Smart-Crop + encode per platform
   ```

**Output:**
```
final_output/
├── master_4k60.mp4           # Master file
├── youtube_4k60.mp4          # YouTube optimized
├── tiktok_1080p.mp4          # TikTok vertical
├── instagram_square.mp4      # Instagram feed
└── audio_only.aac            # Audio track
```

---

## 5. Pipeline Anti-Parallaxe

### 5.1 Displacement Geometry

**Problème:** Une simple texture projetée sur un plan ne gère pas la parallaxe.

**Solution:** Utiliser depth maps pour créer de la vraie géométrie 3D.

```python
# Configuration Displacement
displace_modifier.texture = depth_texture
displace_modifier.strength = 0.5      # Amplitude du relief
displace_modifier.mid_level = 0.5     # Point neutre (gris 50%)
displace_modifier.direction = 'NORMAL'

# Subdivision suffisante
subdivision_modifier.levels = 6        # 64x64 = 4096 faces minimum
```

**Calibration:**
- Strength 0.3: Intérieurs plats (couloirs)
- Strength 0.5: Pièces standard
- Strength 0.8: Scènes avec forte profondeur

### 5.2 Multi-Projection Blending

**Problème:** Une seule projection cause des artefacts lors du mouvement.

**Solution:** Blender 3 projections (début, milieu, fin) avec transition douce.

```python
# Poids des projections selon animation_progress (0→1)

def weight_frame0(progress):
    return max(0, 1 - progress * 2)
    # 1.0 à progress=0, 0.0 à progress>=0.5

def weight_frame50(progress):
    return 1 - abs(progress - 0.5) * 2
    # 0.0 à progress=0, 1.0 à progress=0.5, 0.0 à progress=1

def weight_frame100(progress):
    return max(0, progress * 2 - 1)
    # 0.0 à progress<=0.5, 1.0 à progress=1
```

**Visualisation:**
```
Progress:  0.0   0.25   0.5   0.75   1.0
Frame0:    1.0   0.5    0.0   0.0    0.0
Frame50:   0.0   0.5    1.0   0.5    0.0
Frame100:  0.0   0.0    0.0   0.5    1.0
```

### 5.3 Inpainting de Bordure

**Problème:** La parallaxe révèle des zones non visibles dans la source.

**Solutions:**

1. **Blender Fill (rapide)**
   ```python
   # Extend UV beyond frame
   for uv in mesh.uv_layers.active.data:
       uv.uv = clamp_and_extend(uv.uv, extend_ratio=0.1)
   ```

2. **Stable Diffusion Inpaint (qualité)**
   ```python
   # Pour les gaps importants
   from diffusers import StableDiffusionInpaintPipeline
   
   pipe = StableDiffusionInpaintPipeline.from_pretrained(
       "runwayml/stable-diffusion-inpainting"
   )
   
   inpainted = pipe(
       prompt="seamless interior wall continuation",
       image=frame_with_gap,
       mask_image=gap_mask
   ).images[0]
   ```

---

## 6. Stratégie Anti-Shadowban

### 6.1 Détection Duplicate Content

Les plateformes détectent les duplicates via:
- Hash perceptuel (pHash)
- Fingerprint audio
- Métadonnées EXIF
- Patterns de compression

### 6.2 Contre-mesures

| Technique | Implémentation | Efficacité |
|-----------|----------------|------------|
| Micro color shift | colorbalance ±0.01 | ★★★☆☆ |
| Noise injection | noise=alls=2 | ★★★★☆ |
| Speed variation | setpts ±0.1% | ★★★☆☆ |
| Crop variation | pad/crop 1-2px | ★★★★☆ |
| Audio variation | pitch ±0.5%, reverb | ★★★★★ |
| Re-encoding | Different CRF | ★★☆☆☆ |

### 6.3 Variants System

```python
def generate_variants(master_video, num_variants=5):
    """Génère N variantes uniques d'une même vidéo."""
    variants = []
    
    for i in range(num_variants):
        variant_params = {
            "color_shift": random.uniform(-0.02, 0.02),
            "noise_level": random.randint(1, 3),
            "speed_factor": random.uniform(0.998, 1.002),
            "crop_offset": (random.randint(-2, 2), random.randint(-2, 2)),
            "audio_pitch": random.uniform(0.995, 1.005)
        }
        
        variant = apply_variations(master_video, variant_params)
        variants.append(variant)
    
    return variants
```

### 6.4 Upload Schedule

- Espacer uploads: minimum 4h entre vidéos similaires
- Varier titres et descriptions
- Utiliser différents comptes si volume élevé
- Mixer avec contenu original

---

*Document généré le 2026-02-06*
*Version: 3.1.0*
