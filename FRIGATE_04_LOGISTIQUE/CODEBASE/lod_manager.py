#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate LOGISTIQUE - LOD Manager
Système LOD (Level of Detail) basé sur la distance caméra.

| LOD  | Distance Caméra | Decimate Ratio |
|------|-----------------|----------------|
| LOD0 | < 2m            | 1.0 (full)     |
| LOD1 | 2-5m            | 0.5            |
| LOD2 | > 5m            | 0.25           |
"""

import math
from typing import Any, Optional, Dict, List, Tuple

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class LODManager:
    """
    Gère le système LOD (Level of Detail) pour les assets linkés.
    
    Implémente un système à 3 niveaux via Blender Drivers sur le modifier Decimate:
    - LOD0: Distance < 2m → ratio 1.0 (détail complet)
    - LOD1: Distance 2-5m → ratio 0.5
    - LOD2: Distance > 5m → ratio 0.25
    
    Usage:
        lod_manager = LODManager()
        lod_manager.setup_lod_driver(asset_object, camera)
    """
    
    LOD_THRESHOLDS = {
        "LOD0": {"max_distance": 2.0, "ratio": 1.0},
        "LOD1": {"max_distance": 5.0, "ratio": 0.5},
        "LOD2": {"max_distance": float('inf'), "ratio": 0.25},
    }
    
    DECIMATE_MODIFIER_NAME = "LOD_Decimate"
    LOD_DRIVER_NAME = "lod_distance_driver"
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs LOD
        """
        self.verbose = verbose
        self._setup_count = 0
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"📐 [LODManager] {message}")
    
    def _register_lod_function(self) -> None:
        """
        Enregistre la fonction Python lod_factor() pour les Drivers Blender.
        
        La fonction calcule le ratio Decimate basé sur la distance.
        """
        if not BPY_AVAILABLE:
            return
        
        def lod_factor(distance: float) -> float:
            """
            Calcule le ratio LOD basé sur la distance caméra.
            
            Args:
                distance: Distance entre objet et caméra
                
            Returns:
                Ratio de decimation (0.25 à 1.0)
            """
            if distance < 2.0:
                return 1.0
            elif distance < 5.0:
                t = (distance - 2.0) / 3.0
                return 1.0 - (t * 0.5)
            else:
                return 0.25
        
        if "lod_factor" not in bpy.app.driver_namespace:
            bpy.app.driver_namespace["lod_factor"] = lod_factor
            self._log("Fonction lod_factor() enregistrée dans driver_namespace")
    
    def _add_decimate_modifier(self, obj: Any) -> Any:
        """
        Ajoute un modifier Decimate à l'objet.
        
        Args:
            obj: Objet Blender mesh
            
        Returns:
            Le modifier créé
        """
        if not BPY_AVAILABLE:
            return None
        
        existing = obj.modifiers.get(self.DECIMATE_MODIFIER_NAME)
        if existing:
            return existing
        
        modifier = obj.modifiers.new(name=self.DECIMATE_MODIFIER_NAME, type='DECIMATE')
        modifier.decimate_type = 'COLLAPSE'
        modifier.ratio = 1.0
        modifier.use_collapse_triangulate = True
        
        return modifier
    
    def setup_lod_driver(
        self, 
        asset: Any, 
        camera: Any
    ) -> bool:
        """
        Configure un driver LOD sur l'asset basé sur la distance caméra.
        
        Le driver calcule:
            distance = sqrt((cam.x - obj.x)² + (cam.y - obj.y)² + (cam.z - obj.z)²)
            ratio = lod_factor(distance)
        
        Args:
            asset: Objet Blender (mesh) avec l'asset linké
            camera: Caméra de référence pour la distance
            
        Returns:
            True si driver configuré, False sinon
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - setup LOD impossible")
            return False
        
        if asset is None or asset.type != 'MESH':
            self._log(f"⚠️ Objet invalide ou non-mesh: {asset}")
            return False
        
        self._log(f"Setup LOD driver: {asset.name}")
        
        self._register_lod_function()
        
        modifier = self._add_decimate_modifier(asset)
        if modifier is None:
            return False
        
        try:
            modifier.driver_remove("ratio")
        except:
            pass
        
        fcurve = modifier.driver_add("ratio")
        driver = fcurve.driver
        driver.type = 'SCRIPTED'
        
        var_cam_x = driver.variables.new()
        var_cam_x.name = "cam_x"
        var_cam_x.targets[0].id = camera
        var_cam_x.targets[0].data_path = "location.x"
        
        var_cam_y = driver.variables.new()
        var_cam_y.name = "cam_y"
        var_cam_y.targets[0].id = camera
        var_cam_y.targets[0].data_path = "location.y"
        
        var_cam_z = driver.variables.new()
        var_cam_z.name = "cam_z"
        var_cam_z.targets[0].id = camera
        var_cam_z.targets[0].data_path = "location.z"
        
        var_obj_x = driver.variables.new()
        var_obj_x.name = "obj_x"
        var_obj_x.targets[0].id = asset
        var_obj_x.targets[0].data_path = "location.x"
        
        var_obj_y = driver.variables.new()
        var_obj_y.name = "obj_y"
        var_obj_y.targets[0].id = asset
        var_obj_y.targets[0].data_path = "location.y"
        
        var_obj_z = driver.variables.new()
        var_obj_z.name = "obj_z"
        var_obj_z.targets[0].id = asset
        var_obj_z.targets[0].data_path = "location.z"
        
        driver.expression = (
            "lod_factor(sqrt("
            "(cam_x - obj_x)**2 + "
            "(cam_y - obj_y)**2 + "
            "(cam_z - obj_z)**2"
            "))"
        )
        
        self._setup_count += 1
        self._log(f"  ✓ Driver LOD configuré pour {asset.name}")
        
        return True
    
    def setup_lod_for_collection(
        self, 
        collection_name: str,
        camera: Any
    ) -> int:
        """
        Configure LOD pour tous les objets d'une collection.
        
        Args:
            collection_name: Nom de la collection (ex: "ASSETS_LINKED")
            camera: Caméra de référence
            
        Returns:
            Nombre d'objets configurés
        """
        if not BPY_AVAILABLE:
            return 0
        
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            self._log(f"⚠️ Collection '{collection_name}' non trouvée")
            return 0
        
        count = 0
        for obj in collection.objects:
            if obj.type == 'MESH':
                if self.setup_lod_driver(obj, camera):
                    count += 1
        
        self._log(f"LOD configuré pour {count} objets dans '{collection_name}'")
        return count
    
    def calculate_lod_level(self, distance: float) -> Tuple[str, float]:
        """
        Calcule le niveau LOD et ratio pour une distance donnée.
        
        Args:
            distance: Distance en mètres
            
        Returns:
            Tuple (lod_name, ratio)
        """
        if distance < self.LOD_THRESHOLDS["LOD0"]["max_distance"]:
            return ("LOD0", 1.0)
        elif distance < self.LOD_THRESHOLDS["LOD1"]["max_distance"]:
            t = (distance - 2.0) / 3.0
            ratio = 1.0 - (t * 0.5)
            return ("LOD1", ratio)
        else:
            return ("LOD2", 0.25)
    
    def remove_lod_drivers(self, obj: Any) -> bool:
        """
        Supprime les drivers LOD d'un objet.
        
        Args:
            obj: Objet Blender
            
        Returns:
            True si supprimé, False sinon
        """
        if not BPY_AVAILABLE:
            return False
        
        modifier = obj.modifiers.get(self.DECIMATE_MODIFIER_NAME)
        if modifier:
            try:
                modifier.driver_remove("ratio")
                obj.modifiers.remove(modifier)
                return True
            except:
                pass
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Retourne les statistiques LOD."""
        return {
            "drivers_setup": self._setup_count
        }


def lod_factor_standalone(distance: float) -> float:
    """
    Version standalone de lod_factor pour tests hors Blender.
    
    Args:
        distance: Distance en mètres
        
    Returns:
        Ratio de decimation (0.25 à 1.0)
    """
    if distance < 2.0:
        return 1.0
    elif distance < 5.0:
        t = (distance - 2.0) / 3.0
        return 1.0 - (t * 0.5)
    else:
        return 0.25


if __name__ == "__main__":
    print("=" * 50)
    print("LOD MANAGER - Test Mode")
    print("=" * 50)
    
    lod_manager = LODManager(verbose=True)
    print(f"\n📐 LODManager initialisé (bpy_available={BPY_AVAILABLE})")
    
    print(f"\n🎯 Test calcul LOD:")
    test_distances = [0.5, 1.5, 2.5, 3.5, 4.5, 6.0, 10.0, 50.0]
    
    for d in test_distances:
        lod_name, ratio = lod_manager.calculate_lod_level(d)
        ratio_standalone = lod_factor_standalone(d)
        print(f"   Distance {d:5.1f}m → {lod_name} (ratio={ratio:.2f}, standalone={ratio_standalone:.2f})")
    
    print(f"\n📊 Thresholds:")
    for lod, config in LODManager.LOD_THRESHOLDS.items():
        print(f"   {lod}: max_dist={config['max_distance']}m, ratio={config['ratio']}")
    
    print(f"\n📈 Stats:")
    stats = lod_manager.get_stats()
    print(f"   {stats}")
    
    print("\n✅ Module lod_manager.py fonctionnel")
