#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCÉNOGRAPHE - Opening Cutter
Crée les ouvertures (fenêtres/portes) via Boolean Modifiers.
"""

from typing import Tuple, List, Dict, Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class OpeningCutter:
    """
    Crée les ouvertures via Boolean Modifiers.
    
    Permet de percer des fenêtres et portes dans les murs
    en utilisant des opérations Boolean Difference.
    """
    
    DEFAULT_WINDOW_SIZE = (1.2, 1.0)
    DEFAULT_DOOR_SIZE = (0.9, 2.1)
    WALL_THICKNESS = 0.3
    
    def __init__(self):
        """Initialise le cutter."""
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        print("✂️ OpeningCutter initialisé")
    
    def cut_window(self, 
                   wall, 
                   position: Tuple[float, float, float], 
                   size: Tuple[float, float] = None,
                   apply_modifier: bool = True):
        """
        Crée une ouverture fenêtre dans un mur.
        
        Args:
            wall: Objet mur Blender
            position: (x, y, z) centre de la fenêtre
            size: (width, height) de la fenêtre
            apply_modifier: Appliquer le modifier et supprimer le cutter
        """
        if size is None:
            size = self.DEFAULT_WINDOW_SIZE
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        cutter = bpy.context.active_object
        cutter.name = f"Window_Cutter_{wall.name}"
        
        cutter.scale = (size[0], self.WALL_THICKNESS, size[1])
        
        bpy.context.view_layer.objects.active = wall
        wall.select_set(True)
        cutter.select_set(False)
        
        bool_mod = wall.modifiers.new(name="Boolean_Window", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter
        bool_mod.solver = 'FAST'
        
        if apply_modifier:
            bpy.ops.object.modifier_apply(modifier="Boolean_Window")
            bpy.data.objects.remove(cutter, do_unlink=True)
            print(f"   🪟 Fenêtre coupée dans {wall.name} à {position}")
        else:
            cutter.hide_viewport = True
            cutter.hide_render = True
            print(f"   🪟 Boolean fenêtre ajouté à {wall.name} (non appliqué)")
    
    def cut_door(self, 
                 wall, 
                 position: Tuple[float, float, float], 
                 size: Tuple[float, float] = None,
                 apply_modifier: bool = True):
        """
        Crée une ouverture porte (part du sol).
        
        Args:
            wall: Objet mur Blender
            position: (x, y, z) centre bas de la porte
            size: (width, height) de la porte
            apply_modifier: Appliquer le modifier
        """
        if size is None:
            size = self.DEFAULT_DOOR_SIZE
        
        door_center_z = size[1] / 2
        door_position = (position[0], position[1], door_center_z)
        
        self.cut_window(wall, door_position, size, apply_modifier)
        print(f"   🚪 Porte coupée dans {wall.name}")
    
    def cut_openings_from_masterplan(self, 
                                     walls: Dict[str, Any], 
                                     openings: List[Dict[str, Any]]):
        """
        Coupe toutes les ouvertures définies dans le masterplan.
        
        Args:
            walls: Dict mapping nom -> objet mur Blender
            openings: Liste des ouvertures du masterplan
                Format: [{"type": "window"|"door", "wall": "north", 
                          "position": [x, y, z], "size": [w, h]}]
        """
        if not openings:
            print("   ℹ️ Aucune ouverture à créer")
            return
        
        print(f"✂️ Création de {len(openings)} ouvertures...")
        
        for opening in openings:
            opening_type = opening.get("type", "window")
            wall_name = opening.get("wall", "").lower()
            
            wall_key = None
            for key in walls.keys():
                if wall_name in key.lower():
                    wall_key = key
                    break
            
            if wall_key is None:
                print(f"   ⚠️ Mur '{wall_name}' non trouvé, ouverture ignorée")
                continue
            
            wall = walls[wall_key]
            position = tuple(opening.get("position", [0, 0, 1.5]))
            size = tuple(opening.get("size", None) or 
                        (self.DEFAULT_DOOR_SIZE if opening_type == "door" 
                         else self.DEFAULT_WINDOW_SIZE))
            
            if opening_type == "door":
                self.cut_door(wall, position, size)
            else:
                self.cut_window(wall, position, size)
        
        print(f"✅ Ouvertures créées")
    
    def create_archway(self,
                       wall,
                       position: Tuple[float, float, float],
                       width: float = 1.2,
                       height: float = 2.4,
                       arch_height: float = 0.3,
                       segments: int = 16):
        """
        Crée une arche (ouverture avec voûte).
        
        Args:
            wall: Objet mur Blender
            position: Centre bas de l'arche
            width: Largeur de l'arche
            height: Hauteur totale
            arch_height: Hauteur de la partie voûtée
            segments: Segments pour la courbe
        """
        import math
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        base = bpy.context.active_object
        base.name = "Archway_Base"
        base.scale = (width, self.WALL_THICKNESS, height - arch_height)
        base.location[2] = (height - arch_height) / 2
        
        arch_center_z = height - arch_height
        bpy.ops.mesh.primitive_cylinder_add(
            radius=width / 2,
            depth=self.WALL_THICKNESS,
            vertices=segments,
            location=(position[0], position[1], arch_center_z)
        )
        arch = bpy.context.active_object
        arch.name = "Archway_Arch"
        arch.rotation_euler[0] = math.pi / 2
        
        base.select_set(True)
        arch.select_set(True)
        bpy.context.view_layer.objects.active = base
        bpy.ops.object.join()
        
        cutter = bpy.context.active_object
        cutter.name = "Archway_Cutter"
        
        bpy.context.view_layer.objects.active = wall
        wall.select_set(True)
        cutter.select_set(False)
        
        bool_mod = wall.modifiers.new(name="Boolean_Archway", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter
        bool_mod.solver = 'FAST'
        
        bpy.ops.object.modifier_apply(modifier="Boolean_Archway")
        bpy.data.objects.remove(cutter, do_unlink=True)
        
        print(f"   🏛️ Arche créée dans {wall.name}")
