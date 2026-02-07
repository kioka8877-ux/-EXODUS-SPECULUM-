#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCÉNOGRAPHE - Room Builder
Génère la géométrie de base de la pièce (box room) avec displacement.
"""

import math
from typing import List, Tuple, Dict, Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class RoomBuilder:
    """
    Génère la géométrie de base de la pièce.
    
    Crée 6 surfaces (box room) avec subdivision et displacement
    à partir des depth maps pour obtenir l'effet "blob".
    """
    
    DISPLACEMENT_STRENGTH = 0.5
    DISPLACEMENT_MIDLEVEL = 0.5
    SUBDIVISION_LEVELS = 6
    
    def __init__(self, masterplan: Dict[str, Any]):
        """
        Args:
            masterplan: Dict contenant dimensions_estimate {width_m, depth_m, height_m}
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        self.masterplan = masterplan
        self.dimensions = masterplan.get("dimensions_estimate", masterplan.get("room", {}).get("dimensions", {}))
        
        self.width = self.dimensions.get("width_m", self.dimensions.get("width", 5.0))
        self.depth = self.dimensions.get("depth_m", self.dimensions.get("depth", 5.0))
        self.height = self.dimensions.get("height_m", self.dimensions.get("height", 2.7))
        
        print(f"📐 RoomBuilder initialisé")
        print(f"   Dimensions: {self.width}m x {self.depth}m x {self.height}m")
    
    def create_room_shell(self) -> List:
        """
        Crée les 6 surfaces de la pièce (box room).
        
        Returns:
            Liste des objets Blender créés
        """
        surfaces = []
        
        floor = self._create_surface(
            name="Floor",
            size=(self.width, self.depth),
            location=(0, 0, 0),
            rotation=(0, 0, 0)
        )
        surfaces.append(floor)
        
        ceiling = self._create_surface(
            name="Ceiling",
            size=(self.width, self.depth),
            location=(0, 0, self.height),
            rotation=(math.pi, 0, 0)
        )
        surfaces.append(ceiling)
        
        wall_north = self._create_surface(
            name="Wall_North",
            size=(self.width, self.height),
            location=(0, self.depth / 2, self.height / 2),
            rotation=(math.pi / 2, 0, 0)
        )
        surfaces.append(wall_north)
        
        wall_south = self._create_surface(
            name="Wall_South",
            size=(self.width, self.height),
            location=(0, -self.depth / 2, self.height / 2),
            rotation=(-math.pi / 2, 0, 0)
        )
        surfaces.append(wall_south)
        
        wall_east = self._create_surface(
            name="Wall_East",
            size=(self.depth, self.height),
            location=(self.width / 2, 0, self.height / 2),
            rotation=(math.pi / 2, 0, math.pi / 2)
        )
        surfaces.append(wall_east)
        
        wall_west = self._create_surface(
            name="Wall_West",
            size=(self.depth, self.height),
            location=(-self.width / 2, 0, self.height / 2),
            rotation=(math.pi / 2, 0, -math.pi / 2)
        )
        surfaces.append(wall_west)
        
        print(f"✅ {len(surfaces)} surfaces créées")
        return surfaces
    
    def _create_surface(self, 
                        name: str, 
                        size: Tuple[float, float], 
                        location: Tuple[float, float, float], 
                        rotation: Tuple[float, float, float]):
        """
        Crée un plan subdivisé avec les paramètres spécifiés.
        
        Args:
            name: Nom de la surface
            size: (width, height) de la surface
            location: (x, y, z) position
            rotation: (rx, ry, rz) rotation en radians
            
        Returns:
            Objet Blender créé
        """
        bpy.ops.mesh.primitive_plane_add(size=1, location=location)
        plane = bpy.context.active_object
        plane.name = f"{name}_Displaced"
        
        plane.scale = (size[0], size[1], 1)
        plane.rotation_euler = rotation
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        subsurf = plane.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 0
        subsurf.render_levels = self.SUBDIVISION_LEVELS
        subsurf.subdivision_type = 'SIMPLE'
        
        return plane
    
    def apply_displacement(self, 
                          surface, 
                          depth_map_path: str,
                          strength: Optional[float] = None,
                          midlevel: Optional[float] = None):
        """
        Applique le displacement modifier avec la depth map.
        
        Args:
            surface: Objet Blender surface
            depth_map_path: Chemin vers la depth map PNG 16-bit
            strength: Force du displacement (défaut: DISPLACEMENT_STRENGTH)
            midlevel: Niveau médian (défaut: DISPLACEMENT_MIDLEVEL)
        """
        if strength is None:
            strength = self.DISPLACEMENT_STRENGTH
        if midlevel is None:
            midlevel = self.DISPLACEMENT_MIDLEVEL
        
        tex_name = f"DepthTex_{surface.name}"
        tex = bpy.data.textures.new(name=tex_name, type='IMAGE')
        
        try:
            img = bpy.data.images.load(depth_map_path)
            img.colorspace_settings.name = 'Non-Color'
            tex.image = img
        except Exception as e:
            print(f"⚠️ Erreur chargement depth map: {e}")
            return
        
        subsurf = surface.modifiers.get("Subdivision")
        if subsurf:
            subsurf.levels = self.SUBDIVISION_LEVELS
        
        displace = surface.modifiers.new(name="Displace", type='DISPLACE')
        displace.texture = tex
        displace.strength = strength
        displace.mid_level = midlevel
        displace.texture_coords = 'UV'
        
        print(f"   📊 Displacement appliqué à {surface.name}")
        print(f"      Strength: {strength}, Midlevel: {midlevel}")
    
    def apply_displacement_to_all(self, 
                                  surfaces: List, 
                                  depth_maps_dir: str,
                                  depth_files: Optional[List[str]] = None):
        """
        Applique le displacement à toutes les surfaces.
        
        Args:
            surfaces: Liste des surfaces Blender
            depth_maps_dir: Dossier contenant les depth maps
            depth_files: Liste optionnelle des fichiers à utiliser
        """
        import os
        
        if depth_files is None:
            depth_files = sorted([
                f for f in os.listdir(depth_maps_dir) 
                if f.endswith('.png')
            ])
        
        if not depth_files:
            print("⚠️ Aucune depth map trouvée, displacement ignoré")
            return
        
        primary_depth = os.path.join(depth_maps_dir, depth_files[0])
        
        for surface in surfaces:
            self.apply_displacement(surface, primary_depth)
