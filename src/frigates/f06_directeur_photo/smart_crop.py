#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO - Smart Crop
POI tracking + sensor shift pour orienter le regard caméra vers les zones d'intérêt.

Utilise la heatmap POI du masterplan pour guider subtilement la caméra
vers les meubles et éléments importants de la scène.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


MAX_SENSOR_SHIFT = 0.15
POI_TRACKING_SMOOTHNESS = 0.7


class SmartCrop:
    """
    Utilise les POI (Points d'Intérêt) du masterplan pour orienter
    subtilement le regard de la caméra vers les meubles importants.
    
    Technique: Sensor Shift
    - Équivalent à un "pan" sans bouger physiquement la caméra
    - Permet de recentrer la composition sur les éléments clés
    - Maximum ±15% du sensor pour éviter distorsion
    
    Usage:
        smart_crop = SmartCrop()
        poi_heatmap = smart_crop.load_poi_heatmap("/path/to/masterplan.json")
        poi_center = smart_crop.calculate_poi_center(poi_heatmap)
        smart_crop.apply_sensor_shift(camera, poi_center)
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs
        """
        self.verbose = verbose
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"👁️ [SmartCrop] {message}")
    
    def load_poi_heatmap(self, masterplan_path: str) -> Dict:
        """
        Charge la heatmap POI depuis masterplan.json.
        
        Args:
            masterplan_path: Chemin vers le fichier masterplan.json
            
        Returns:
            Dict contenant les données POI ou structure vide
        """
        try:
            with open(masterplan_path, 'r') as f:
                data = json.load(f)
            
            masterplan = data.get('masterplan', data)
            poi_heatmap = masterplan.get('poi_heatmap', {})
            
            self._log(f"✓ Heatmap POI chargée depuis {masterplan_path}")
            
            if 'data' in poi_heatmap:
                resolution = poi_heatmap.get('resolution', [32, 32])
                self._log(f"  Résolution: {resolution[0]}x{resolution[1]}")
            elif 'points' in poi_heatmap:
                self._log(f"  Points d'intérêt: {len(poi_heatmap['points'])}")
            else:
                self._log("  ⚠️ Format heatmap non reconnu - utilisation centre")
            
            return poi_heatmap
            
        except FileNotFoundError:
            self._log(f"⚠️ Fichier masterplan non trouvé: {masterplan_path}")
            return {}
        except json.JSONDecodeError as e:
            self._log(f"⚠️ Erreur parsing JSON: {e}")
            return {}
    
    def calculate_poi_center(
        self,
        poi_heatmap: Dict,
        frame: int = 0
    ) -> Tuple[float, float]:
        """
        Calcule le centre pondéré des POI.
        
        Supporte plusieurs formats de heatmap:
        1. Grille 2D (data + resolution)
        2. Liste de points avec poids
        3. Centre simple (x, y)
        
        Args:
            poi_heatmap: Dict heatmap depuis load_poi_heatmap
            frame: Frame actuelle (pour animations temporelles)
            
        Returns:
            (x, y) normalisé [0, 1] où (0.5, 0.5) = centre
        """
        if 'data' in poi_heatmap:
            return self._calculate_center_from_grid(poi_heatmap)
        
        if 'points' in poi_heatmap:
            return self._calculate_center_from_points(poi_heatmap['points'])
        
        if 'center' in poi_heatmap:
            center = poi_heatmap['center']
            return (center.get('x', 0.5), center.get('y', 0.5))
        
        if 'x' in poi_heatmap and 'y' in poi_heatmap:
            return (poi_heatmap['x'], poi_heatmap['y'])
        
        self._log("  ⚠️ Aucune donnée POI - retour au centre")
        return (0.5, 0.5)
    
    def _calculate_center_from_grid(self, poi_heatmap: Dict) -> Tuple[float, float]:
        """Calcule le centre pondéré depuis une grille 2D."""
        grid = poi_heatmap['data']
        resolution = poi_heatmap.get('resolution', [len(grid[0]) if grid else 32, len(grid)])
        
        total_weight = 0.0
        cx, cy = 0.0, 0.0
        
        for y, row in enumerate(grid):
            for x, weight in enumerate(row):
                if weight > 0:
                    cx += x * weight
                    cy += y * weight
                    total_weight += weight
        
        if total_weight > 0:
            cx = cx / total_weight / (resolution[0] - 1) if resolution[0] > 1 else 0.5
            cy = cy / total_weight / (resolution[1] - 1) if resolution[1] > 1 else 0.5
            return (cx, cy)
        
        return (0.5, 0.5)
    
    def _calculate_center_from_points(
        self,
        points: List[Dict]
    ) -> Tuple[float, float]:
        """Calcule le centre pondéré depuis une liste de points."""
        if not points:
            return (0.5, 0.5)
        
        total_weight = 0.0
        cx, cy = 0.0, 0.0
        
        for point in points:
            x = point.get('x', 0.5)
            y = point.get('y', 0.5)
            weight = point.get('weight', point.get('importance', 1.0))
            
            cx += x * weight
            cy += y * weight
            total_weight += weight
        
        if total_weight > 0:
            return (cx / total_weight, cy / total_weight)
        
        return (0.5, 0.5)
    
    def apply_sensor_shift(
        self,
        camera: Any,
        poi_center: Tuple[float, float],
        max_shift: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Applique un décalage du sensor pour recentrer sur le POI.
        
        Le shift est calculé depuis le centre de l'image (0.5, 0.5)
        et limité à MAX_SENSOR_SHIFT pour éviter les distorsions.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            poi_center: (x, y) normalisé du centre POI
            max_shift: Override du shift maximum
            
        Returns:
            (shift_x, shift_y) appliqués
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - sensor shift impossible")
            return (0.0, 0.0)
        
        max_s = max_shift if max_shift is not None else MAX_SENSOR_SHIFT
        frame_center = (0.5, 0.5)
        
        offset_x = (poi_center[0] - frame_center[0]) * max_s * 2
        offset_y = (poi_center[1] - frame_center[1]) * max_s * 2
        
        offset_x = max(-max_s, min(max_s, offset_x))
        offset_y = max(-max_s, min(max_s, offset_y))
        
        camera.data.shift_x = offset_x
        camera.data.shift_y = offset_y
        
        self._log(f"✓ Sensor shift appliqué sur {camera.name}")
        self._log(f"  POI center: ({poi_center[0]:.3f}, {poi_center[1]:.3f})")
        self._log(f"  Shift: ({offset_x:.4f}, {offset_y:.4f})")
        
        return (offset_x, offset_y)
    
    def animate_sensor_shift(
        self,
        camera: Any,
        poi_sequence: List[Tuple[float, float]],
        duration_frames: int,
        smoothness: Optional[float] = None
    ) -> int:
        """
        Anime le sensor shift sur la durée si le POI se déplace.
        
        Applique un smoothing pour éviter les mouvements brusques.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            poi_sequence: Liste de (x, y) pour chaque segment temporel
            duration_frames: Nombre total de frames
            smoothness: Facteur de lissage 0-1 (0=instant, 1=statique)
            
        Returns:
            Nombre de keyframes créées
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - animation impossible")
            return 0
        
        smooth = smoothness if smoothness is not None else POI_TRACKING_SMOOTHNESS
        
        if not poi_sequence:
            self._log("⚠️ Séquence POI vide - pas d'animation")
            return 0
        
        if not camera.data.animation_data:
            camera.data.animation_data_create()
        if not camera.data.animation_data.action:
            camera.data.animation_data.action = bpy.data.actions.new(
                name=f"SmartCrop_{camera.name}"
            )
        
        shift_x_fcurve = camera.data.animation_data.action.fcurves.new(
            data_path='shift_x'
        )
        shift_y_fcurve = camera.data.animation_data.action.fcurves.new(
            data_path='shift_y'
        )
        
        frames_per_segment = max(1, duration_frames // len(poi_sequence))
        
        prev_shift_x, prev_shift_y = 0.0, 0.0
        keyframe_count = 0
        
        for i, poi_center in enumerate(poi_sequence):
            frame = i * frames_per_segment
            
            target_x = (poi_center[0] - 0.5) * MAX_SENSOR_SHIFT * 2
            target_y = (poi_center[1] - 0.5) * MAX_SENSOR_SHIFT * 2
            
            target_x = max(-MAX_SENSOR_SHIFT, min(MAX_SENSOR_SHIFT, target_x))
            target_y = max(-MAX_SENSOR_SHIFT, min(MAX_SENSOR_SHIFT, target_y))
            
            shift_x = prev_shift_x + (1 - smooth) * (target_x - prev_shift_x)
            shift_y = prev_shift_y + (1 - smooth) * (target_y - prev_shift_y)
            
            shift_x_fcurve.keyframe_points.insert(frame, shift_x)
            shift_y_fcurve.keyframe_points.insert(frame, shift_y)
            keyframe_count += 2
            
            prev_shift_x, prev_shift_y = shift_x, shift_y
        
        for fc in [shift_x_fcurve, shift_y_fcurve]:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
        
        self._log(f"✓ Animation sensor shift créée sur {camera.name}")
        self._log(f"  Segments POI: {len(poi_sequence)}")
        self._log(f"  Keyframes: {keyframe_count}")
        self._log(f"  Smoothness: {smooth}")
        
        return keyframe_count
    
    def create_poi_from_objects(
        self,
        objects: List[Any],
        camera: Any
    ) -> List[Dict]:
        """
        Génère une liste de POI depuis des objets Blender.
        
        Projette les positions 3D des objets vers des coordonnées
        normalisées dans le champ de vision de la caméra.
        
        Args:
            objects: Liste d'objets bpy.types.Object
            camera: bpy.types.Object de type CAMERA
            
        Returns:
            Liste de dicts {'x': float, 'y': float, 'weight': float, 'name': str}
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible")
            return []
        
        from bpy_extras.object_utils import world_to_camera_view
        
        scene = bpy.context.scene
        poi_list = []
        
        for obj in objects:
            try:
                coord = world_to_camera_view(scene, camera, obj.location)
                
                if 0 <= coord.x <= 1 and 0 <= coord.y <= 1 and coord.z > 0:
                    weight = 1.0
                    if hasattr(obj, 'get'):
                        weight = obj.get('poi_weight', obj.get('importance', 1.0))
                    
                    poi_list.append({
                        'x': coord.x,
                        'y': coord.y,
                        'weight': weight,
                        'name': obj.name
                    })
                    
            except Exception as e:
                self._log(f"  ⚠️ Erreur projection {obj.name}: {e}")
        
        self._log(f"✓ {len(poi_list)} POI générés depuis {len(objects)} objets")
        return poi_list
    
    def get_shift_info(self, camera: Any) -> Dict:
        """
        Retourne les informations de shift actuelles de la caméra.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            
        Returns:
            Dict avec shift_x, shift_y et infos animation
        """
        if not BPY_AVAILABLE:
            return {"error": "bpy non disponible"}
        
        info = {
            "name": camera.name,
            "shift_x": camera.data.shift_x,
            "shift_y": camera.data.shift_y,
            "has_animation": False,
            "keyframe_count": 0
        }
        
        if camera.data.animation_data and camera.data.animation_data.action:
            for fc in camera.data.animation_data.action.fcurves:
                if 'shift' in fc.data_path:
                    info["has_animation"] = True
                    info["keyframe_count"] += len(fc.keyframe_points)
        
        return info


if __name__ == "__main__":
    print("=" * 50)
    print("👁️ SMART CROP - Test Mode")
    print("=" * 50)
    
    print(f"\n📋 Configuration:")
    print(f"   MAX_SENSOR_SHIFT: ±{MAX_SENSOR_SHIFT} ({MAX_SENSOR_SHIFT*100:.0f}%)")
    print(f"   POI_TRACKING_SMOOTHNESS: {POI_TRACKING_SMOOTHNESS}")
    print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
    
    smart_crop = SmartCrop(verbose=True)
    print(f"\n✅ SmartCrop initialisé")
    
    print("\n🧪 Test calcul POI depuis grille:")
    mock_heatmap = {
        'data': [
            [0.1, 0.2, 0.1],
            [0.3, 0.8, 0.3],
            [0.1, 0.2, 0.1]
        ],
        'resolution': [3, 3]
    }
    center = smart_crop.calculate_poi_center(mock_heatmap)
    print(f"   Grille 3x3 avec pic au centre")
    print(f"   Centre calculé: ({center[0]:.3f}, {center[1]:.3f})")
    print(f"   Attendu: ~(0.5, 0.5)")
    
    print("\n🧪 Test calcul POI depuis points:")
    mock_points = {
        'points': [
            {'x': 0.2, 'y': 0.3, 'weight': 1.0},
            {'x': 0.8, 'y': 0.7, 'weight': 3.0},
        ]
    }
    center = smart_crop.calculate_poi_center(mock_points)
    print(f"   2 points: poids 1 à (0.2, 0.3), poids 3 à (0.8, 0.7)")
    print(f"   Centre pondéré: ({center[0]:.3f}, {center[1]:.3f})")
    
    if BPY_AVAILABLE and bpy.context.scene.camera:
        print("\n🎬 Test avec scène Blender:")
        cam = bpy.context.scene.camera
        smart_crop.apply_sensor_shift(cam, (0.6, 0.55))
        info = smart_crop.get_shift_info(cam)
        print(f"   Info shift: {info}")
    
    print("\n✅ Module smart_crop.py fonctionnel")
