#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PROJECTIONNISTE - UV Projector
Gère la projection UV depuis les caméras sur les objets mesh.
"""

from typing import List, Dict, Any, Optional
import math

try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None
    bmesh = None
    Vector = None
    Matrix = None


class UVProjector:
    """
    Gère la projection UV depuis les caméras.
    
    Projette les coordonnées UV sur les mesh depuis la perspective
    de chaque caméra de projection pour créer les UV layers nécessaires
    au multi-projection shader.
    """
    
    UV_PREFIX = "UV_Projection_"
    
    def __init__(self):
        """Initialise le projecteur UV."""
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        print("🎯 UVProjector initialisé")
    
    def project_from_camera(
        self, 
        obj: Any,
        camera: Any,
        uv_name: str,
        scale_to_bounds: bool = True
    ) -> str:
        """
        Projette les UVs depuis une caméra sur un objet.
        
        Args:
            obj: Objet mesh Blender cible
            camera: Caméra de projection Blender
            uv_name: Nom de l'UV layer à créer
            scale_to_bounds: Ajuster les UVs aux limites [0,1]
            
        Returns:
            Nom de l'UV layer créé
        """
        if obj.type != 'MESH':
            print(f"   ⚠️ {obj.name} n'est pas un mesh, ignoré")
            return None
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        if uv_name not in obj.data.uv_layers:
            obj.data.uv_layers.new(name=uv_name)
        obj.data.uv_layers.active = obj.data.uv_layers[uv_name]
        
        self._project_uvs_from_camera_view(obj, camera, uv_name, scale_to_bounds)
        
        return uv_name
    
    def _project_uvs_from_camera_view(
        self,
        obj: Any,
        camera: Any,
        uv_name: str,
        scale_to_bounds: bool = True
    ):
        """
        Projection manuelle des UVs depuis la vue caméra.
        
        Calcule les coordonnées UV en projetant chaque vertex
        depuis la perspective de la caméra.
        """
        mesh = obj.data
        
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        uv_layer = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)
        
        cam_data = camera.data
        cam_matrix = camera.matrix_world.inverted()
        
        render = bpy.context.scene.render
        aspect_ratio = render.resolution_x / render.resolution_y
        
        if cam_data.type == 'PERSP':
            fov = 2 * math.atan(cam_data.sensor_width / (2 * cam_data.lens))
        else:
            fov = math.radians(90)
        
        half_fov = fov / 2
        
        uv_coords = []
        
        for face in bm.faces:
            for loop in face.loops:
                world_co = obj.matrix_world @ loop.vert.co
                
                cam_co = cam_matrix @ world_co
                
                if cam_co.z >= 0:
                    u = 0.5
                    v = 0.5
                else:
                    x_proj = cam_co.x / (-cam_co.z)
                    y_proj = cam_co.y / (-cam_co.z)
                    
                    fov_scale = math.tan(half_fov)
                    
                    u = (x_proj / (fov_scale * aspect_ratio) + 1) / 2
                    v = (y_proj / fov_scale + 1) / 2
                
                loop[uv_layer].uv = (u, v)
                uv_coords.append((u, v))
        
        if scale_to_bounds and uv_coords:
            self._normalize_uvs(bm, uv_layer, uv_coords)
        
        bm.to_mesh(mesh)
        bm.free()
        
        mesh.update()
    
    def _normalize_uvs(self, bm, uv_layer, uv_coords: List):
        """Normalise les UVs pour qu'ils restent dans [0, 1]."""
        if not uv_coords:
            return
        
        min_u = min(uv[0] for uv in uv_coords)
        max_u = max(uv[0] for uv in uv_coords)
        min_v = min(uv[1] for uv in uv_coords)
        max_v = max(uv[1] for uv in uv_coords)
        
        range_u = max_u - min_u if max_u != min_u else 1
        range_v = max_v - min_v if max_v != min_v else 1
        
        for face in bm.faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                new_u = (uv[0] - min_u) / range_u
                new_v = (uv[1] - min_v) / range_v
                loop[uv_layer].uv = (new_u, new_v)
    
    def project_from_camera_blender_op(
        self, 
        obj: Any,
        camera: Any,
        uv_name: str
    ) -> str:
        """
        Projette les UVs en utilisant l'opérateur Blender natif.
        
        Cette méthode nécessite un contexte graphique complet
        et ne fonctionne pas en mode headless pur.
        
        Args:
            obj: Objet mesh Blender cible
            camera: Caméra de projection Blender
            uv_name: Nom de l'UV layer à créer
            
        Returns:
            Nom de l'UV layer créé ou None si échec
        """
        if obj.type != 'MESH':
            return None
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        if uv_name not in obj.data.uv_layers:
            obj.data.uv_layers.new(name=uv_name)
        obj.data.uv_layers.active = obj.data.uv_layers[uv_name]
        
        original_camera = bpy.context.scene.camera
        bpy.context.scene.camera = camera
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        try:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region}
                            with bpy.context.temp_override(**override):
                                bpy.ops.view3d.view_camera()
                                bpy.ops.uv.project_from_view(camera_bounds=True, scale_to_bounds=True)
                            break
                    break
        except Exception as e:
            print(f"   ⚠️ Blender UV project operator failed: {e}")
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.scene.camera = original_camera
            return self.project_from_camera(obj, camera, uv_name)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.camera = original_camera
        
        return uv_name
    
    def project_all_keyframes(
        self, 
        objects: List,
        cameras: List,
        use_blender_op: bool = False
    ) -> Dict[str, List[str]]:
        """
        Projette les 3 keyframes sur tous les objets.
        
        Args:
            objects: Liste des objets mesh à projeter
            cameras: Liste des 3 caméras de projection
            use_blender_op: Utiliser l'opérateur Blender natif (nécessite GUI)
            
        Returns:
            Dict {object_name: [uv_layer_0, uv_layer_1, uv_layer_2]}
        """
        results = {}
        
        print(f"\n📐 Projection UV sur {len(objects)} objets")
        
        for obj in objects:
            if obj.type != 'MESH':
                continue
            
            results[obj.name] = []
            
            for i, camera in enumerate(cameras):
                uv_name = f"{self.UV_PREFIX}{i}"
                
                if use_blender_op:
                    created_uv = self.project_from_camera_blender_op(obj, camera, uv_name)
                else:
                    created_uv = self.project_from_camera(obj, camera, uv_name)
                
                if created_uv:
                    results[obj.name].append(created_uv)
            
            print(f"   ✓ {obj.name}: {len(results[obj.name])} UV layers")
        
        total_uvs = sum(len(uvs) for uvs in results.values())
        print(f"✅ Total UV layers créés: {total_uvs}")
        
        return results
    
    def verify_uv_layers(self, obj: Any, expected_count: int = 3) -> bool:
        """
        Vérifie que l'objet possède les UV layers de projection attendus.
        
        Args:
            obj: Objet mesh à vérifier
            expected_count: Nombre d'UV layers attendus
            
        Returns:
            True si toutes les UV layers existent
        """
        if obj.type != 'MESH':
            return False
        
        existing = [uv.name for uv in obj.data.uv_layers 
                   if uv.name.startswith(self.UV_PREFIX)]
        
        return len(existing) >= expected_count
    
    def get_uv_layer_names(self, keyframe_count: int = 3) -> List[str]:
        """
        Retourne les noms standardisés des UV layers.
        
        Args:
            keyframe_count: Nombre de keyframes
            
        Returns:
            Liste des noms d'UV layers
        """
        return [f"{self.UV_PREFIX}{i}" for i in range(keyframe_count)]
