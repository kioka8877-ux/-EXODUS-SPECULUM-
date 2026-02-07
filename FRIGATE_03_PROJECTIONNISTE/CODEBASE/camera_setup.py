#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PROJECTIONNISTE - Camera Setup
Configure les caméras de projection pour les 3 keyframes.
"""

import math
from typing import List, Tuple, Dict, Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class CameraSetup:
    """
    Configure les caméras de projection pour les 3 keyframes.
    
    Estime les positions caméra basées sur le type de mouvement
    détecté dans le masterplan et crée les caméras Blender correspondantes.
    """
    
    DEFAULT_FOV = 35
    DEFAULT_SENSOR_WIDTH = 36
    DEFAULT_CAMERA_HEIGHT_RATIO = 0.6
    
    def __init__(self, room_dimensions: Dict[str, float]):
        """
        Args:
            room_dimensions: Dict contenant width_m, depth_m, height_m
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        self.width = room_dimensions.get("width_m", room_dimensions.get("width", 5.0))
        self.depth = room_dimensions.get("depth_m", room_dimensions.get("depth", 5.0))
        self.height = room_dimensions.get("height_m", room_dimensions.get("height", 2.7))
        
        print(f"📷 CameraSetup initialisé")
        print(f"   Room: {self.width}m x {self.depth}m x {self.height}m")
    
    def estimate_camera_path(self, movement_type: str = "linear_forward") -> List[Tuple]:
        """
        Estime les positions caméra pour les 3 keyframes.
        
        Args:
            movement_type: Type de mouvement détecté
                - linear_forward: Mouvement linéaire vers l'avant
                - linear_backward: Mouvement linéaire vers l'arrière
                - pan_left: Panoramique gauche
                - pan_right: Panoramique droite
                - orbit_cw: Orbite horaire
                - orbit_ccw: Orbite anti-horaire
                - static: Caméra fixe
                - zoom_in: Zoom vers l'avant
                - zoom_out: Zoom vers l'arrière
                
        Returns:
            Liste de 3 tuples (location, rotation_euler) pour keyframes 0%, 50%, 100%
        """
        cam_height = self.height * self.DEFAULT_CAMERA_HEIGHT_RATIO
        
        start_loc = (0, -self.depth / 2 + 0.5, cam_height)
        start_rot = (math.radians(80), 0, 0)
        
        movement_handlers = {
            "linear_forward": self._path_linear_forward,
            "linear_backward": self._path_linear_backward,
            "pan_left": self._path_pan_left,
            "pan_right": self._path_pan_right,
            "orbit_cw": self._path_orbit_cw,
            "orbit_ccw": self._path_orbit_ccw,
            "static": self._path_static,
            "zoom_in": self._path_zoom_in,
            "zoom_out": self._path_zoom_out,
        }
        
        handler = movement_handlers.get(movement_type, self._path_linear_forward)
        positions = handler(cam_height)
        
        print(f"   Movement type: {movement_type}")
        print(f"   Generated {len(positions)} camera positions")
        
        return positions
    
    def _path_linear_forward(self, cam_height: float) -> List[Tuple]:
        """Mouvement linéaire vers l'avant (entrée vers fond de la pièce)."""
        return [
            ((0, -self.depth / 2 + 0.5, cam_height), (math.radians(80), 0, 0)),
            ((0, 0, cam_height), (math.radians(85), 0, 0)),
            ((0, self.depth / 2 - 1.0, cam_height), (math.radians(90), 0, 0)),
        ]
    
    def _path_linear_backward(self, cam_height: float) -> List[Tuple]:
        """Mouvement linéaire vers l'arrière."""
        forward = self._path_linear_forward(cam_height)
        return list(reversed(forward))
    
    def _path_pan_left(self, cam_height: float) -> List[Tuple]:
        """Panoramique de droite vers gauche."""
        center_y = 0
        return [
            ((self.width / 3, center_y, cam_height), (math.radians(85), 0, math.radians(-30))),
            ((0, center_y, cam_height), (math.radians(85), 0, 0)),
            ((-self.width / 3, center_y, cam_height), (math.radians(85), 0, math.radians(30))),
        ]
    
    def _path_pan_right(self, cam_height: float) -> List[Tuple]:
        """Panoramique de gauche vers droite."""
        pan_left = self._path_pan_left(cam_height)
        return list(reversed(pan_left))
    
    def _path_orbit_cw(self, cam_height: float) -> List[Tuple]:
        """Orbite horaire autour du centre."""
        radius = min(self.width, self.depth) / 2.5
        center = (0, 0, 0)
        return [
            ((radius, 0, cam_height), (math.radians(85), 0, math.radians(-90))),
            ((0, radius, cam_height), (math.radians(85), 0, math.radians(180))),
            ((-radius, 0, cam_height), (math.radians(85), 0, math.radians(90))),
        ]
    
    def _path_orbit_ccw(self, cam_height: float) -> List[Tuple]:
        """Orbite anti-horaire autour du centre."""
        orbit_cw = self._path_orbit_cw(cam_height)
        return list(reversed(orbit_cw))
    
    def _path_static(self, cam_height: float) -> List[Tuple]:
        """Caméra fixe avec léger mouvement simulé."""
        base_loc = (0, -self.depth / 3, cam_height)
        base_rot = (math.radians(85), 0, 0)
        return [
            (base_loc, base_rot),
            (base_loc, base_rot),
            (base_loc, base_rot),
        ]
    
    def _path_zoom_in(self, cam_height: float) -> List[Tuple]:
        """Zoom in (rapprochement)."""
        base_rot = (math.radians(85), 0, 0)
        return [
            ((0, -self.depth / 2 + 0.5, cam_height), base_rot),
            ((0, -self.depth / 4, cam_height), base_rot),
            ((0, 0, cam_height), base_rot),
        ]
    
    def _path_zoom_out(self, cam_height: float) -> List[Tuple]:
        """Zoom out (éloignement)."""
        zoom_in = self._path_zoom_in(cam_height)
        return list(reversed(zoom_in))
    
    def create_projection_cameras(
        self, 
        positions: List[Tuple],
        fov: Optional[float] = None,
        sensor_width: Optional[float] = None
    ) -> List:
        """
        Crée les 3 caméras de projection dans Blender.
        
        Args:
            positions: Liste de (location, rotation_euler) tuples
            fov: Focale en mm (défaut: 35mm)
            sensor_width: Largeur sensor en mm (défaut: 36mm)
            
        Returns:
            Liste des objets Camera Blender créés
        """
        if fov is None:
            fov = self.DEFAULT_FOV
        if sensor_width is None:
            sensor_width = self.DEFAULT_SENSOR_WIDTH
        
        cameras = []
        
        for i, (loc, rot) in enumerate(positions):
            bpy.ops.object.camera_add(location=loc, rotation=rot)
            cam = bpy.context.active_object
            cam.name = f"Projection_Camera_{i}"
            
            cam.data.lens = fov
            cam.data.sensor_width = sensor_width
            
            cam.data.display_size = 0.5
            
            cam["keyframe_index"] = i
            cam["keyframe_percent"] = i * 50
            
            cameras.append(cam)
            
            print(f"   📷 Created {cam.name} at {loc}")
        
        if cameras:
            cameras[0]["animation_progress"] = 0.0
            cameras[0].id_properties_ensure()
            cameras[0].id_properties_ui("animation_progress").update(
                min=0.0,
                max=1.0,
                soft_min=0.0,
                soft_max=1.0,
                description="Animation progress for projection blending (0.0 to 1.0)"
            )
        
        print(f"✅ {len(cameras)} projection cameras created")
        return cameras
    
    def create_camera_collection(self, cameras: List) -> Any:
        """
        Crée une collection pour les caméras de projection.
        
        Args:
            cameras: Liste des caméras à organiser
            
        Returns:
            Collection Blender créée
        """
        collection_name = "PROJECTION_CAMERAS"
        
        if collection_name in bpy.data.collections:
            cam_collection = bpy.data.collections[collection_name]
        else:
            cam_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(cam_collection)
        
        for cam in cameras:
            for col in cam.users_collection:
                col.objects.unlink(cam)
            cam_collection.objects.link(cam)
        
        print(f"   📁 Cameras organized in collection: {collection_name}")
        return cam_collection
    
    def estimate_fov_from_video_metadata(
        self, 
        video_width: int = 1920, 
        video_height: int = 1080,
        hfov_estimate: Optional[float] = None
    ) -> float:
        """
        Estime la focale basée sur les métadonnées vidéo.
        
        Args:
            video_width: Largeur vidéo en pixels
            video_height: Hauteur vidéo en pixels
            hfov_estimate: Estimation HFOV en degrés (optionnel)
            
        Returns:
            Focale estimée en mm
        """
        if hfov_estimate:
            focal_length = self.DEFAULT_SENSOR_WIDTH / (2 * math.tan(math.radians(hfov_estimate / 2)))
        else:
            aspect_ratio = video_width / video_height
            if aspect_ratio > 1.7:
                focal_length = 28
            elif aspect_ratio > 1.3:
                focal_length = 35
            else:
                focal_length = 50
        
        focal_length = max(10, min(200, focal_length))
        
        print(f"   📐 Estimated focal length: {focal_length}mm")
        return focal_length
