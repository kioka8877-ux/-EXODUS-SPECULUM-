#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCÉNOGRAPHE - Proxy Generator
Génère les proxies Ghost pour les meubles détectés.
"""

from typing import List, Dict, Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class ProxyGenerator:
    """
    Génère les proxies Ghost pour les meubles détectés.
    
    Les proxies sont des primitives simples (cubes/cylindres)
    positionnées selon le masterplan, avec custom properties
    pour identification par F05-LOGISTIQUE.
    """
    
    PROXY_SHAPES = {
        "sofa": "CUBE",
        "couch": "CUBE",
        "bed": "CUBE",
        "table": "CUBE",
        "dining_table": "CUBE",
        "coffee_table": "CUBE",
        "desk": "CUBE",
        "chair": "CUBE",
        "armchair": "CUBE",
        "cabinet": "CUBE",
        "wardrobe": "CUBE",
        "dresser": "CUBE",
        "shelf": "CUBE",
        "bookshelf": "CUBE",
        "tv_stand": "CUBE",
        "nightstand": "CUBE",
        "lamp": "CYLINDER",
        "floor_lamp": "CYLINDER",
        "table_lamp": "CYLINDER",
        "vase": "CYLINDER",
        "plant": "CYLINDER",
        "potted_plant": "CYLINDER",
        "stool": "CYLINDER",
        "ottoman": "CUBE",
        "rug": "CUBE",
        "mirror": "CUBE",
        "tv": "CUBE",
        "unknown": "CUBE",
    }
    
    PROXY_MATERIAL_NAME = "Ghost_Proxy_Material"
    
    def __init__(self, room_dimensions: Dict[str, Any]):
        """
        Args:
            room_dimensions: Dict avec width_m, depth_m, height_m
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        self.room_width = room_dimensions.get("width_m", room_dimensions.get("width", 5.0))
        self.room_depth = room_dimensions.get("depth_m", room_dimensions.get("depth", 5.0))
        self.room_height = room_dimensions.get("height_m", room_dimensions.get("height", 2.7))
        
        self.proxy_material = self._create_proxy_material()
        
        print(f"🎭 ProxyGenerator initialisé")
        print(f"   Room: {self.room_width}m x {self.room_depth}m x {self.room_height}m")
    
    def _create_proxy_material(self):
        """Crée un matériau semi-transparent pour les proxies."""
        if self.PROXY_MATERIAL_NAME in bpy.data.materials:
            return bpy.data.materials[self.PROXY_MATERIAL_NAME]
        
        mat = bpy.data.materials.new(name=self.PROXY_MATERIAL_NAME)
        mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 1.0, 1.0)
        bsdf.inputs['Alpha'].default_value = 0.3
        
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'
        
        return mat
    
    def create_proxy(self, furniture: Dict[str, Any]) -> Any:
        """
        Crée un proxy pour un meuble.
        
        Args:
            furniture: Dict avec type, position_x, position_y, dimensions_estimate
                - position_x/y: valeurs normalisées [0, 1]
                - dimensions_estimate: [width, depth, height] en mètres
            
        Returns:
            Objet Blender avec custom properties ghost_proxy
        """
        ftype = furniture.get("type", "unknown").lower()
        shape = self.PROXY_SHAPES.get(ftype, "CUBE")
        
        pos_x_norm = furniture.get("position_x", furniture.get("x", 0.5))
        pos_y_norm = furniture.get("position_y", furniture.get("y", 0.5))
        
        pos_x = (pos_x_norm - 0.5) * self.room_width
        pos_y = (pos_y_norm - 0.5) * self.room_depth
        
        dims = furniture.get("dimensions_estimate", furniture.get("dimensions", [1.0, 1.0, 1.0]))
        if isinstance(dims, dict):
            dims = [
                dims.get("width", 1.0),
                dims.get("depth", 1.0),
                dims.get("height", 1.0)
            ]
        
        while len(dims) < 3:
            dims.append(1.0)
        
        pos_z = dims[2] / 2
        
        if shape == "CUBE":
            bpy.ops.mesh.primitive_cube_add(size=1, location=(pos_x, pos_y, pos_z))
        else:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.5, 
                depth=1, 
                location=(pos_x, pos_y, pos_z)
            )
        
        obj = bpy.context.active_object
        
        type_clean = ftype.replace(" ", "_").replace("-", "_").capitalize()
        obj.name = f"Proxy_{type_clean}"
        
        obj.scale = (dims[0], dims[1], dims[2])
        
        obj["ghost_proxy"] = True
        obj["proxy_type"] = ftype
        obj["original_color"] = furniture.get("color", "unknown")
        obj["confidence"] = furniture.get("confidence", 0.5)
        obj["position_normalized"] = [pos_x_norm, pos_y_norm]
        obj["dimensions_estimate"] = dims
        
        if obj.data.materials:
            obj.data.materials[0] = self.proxy_material
        else:
            obj.data.materials.append(self.proxy_material)
        
        obj.display_type = 'WIRE'
        
        return obj
    
    def generate_all_proxies(self, furniture_list: List[Dict[str, Any]]) -> List:
        """
        Génère tous les proxies depuis la liste du masterplan.
        
        Args:
            furniture_list: Liste de dicts furniture du masterplan
            
        Returns:
            Liste des objets Blender proxies créés
        """
        proxies = []
        
        print(f"🎭 Génération de {len(furniture_list)} proxies...")
        
        for idx, furniture in enumerate(furniture_list):
            proxy = self.create_proxy(furniture)
            proxies.append(proxy)
            
            ftype = furniture.get("type", "unknown")
            print(f"   [{idx+1}/{len(furniture_list)}] {proxy.name} ({ftype})")
        
        print(f"✅ {len(proxies)} proxies générés")
        return proxies
    
    def get_proxy_stats(self, proxies: List) -> Dict[str, Any]:
        """
        Retourne des statistiques sur les proxies générés.
        
        Args:
            proxies: Liste des objets proxy
            
        Returns:
            Dict avec statistiques
        """
        stats = {
            "total": len(proxies),
            "by_type": {},
            "by_shape": {"CUBE": 0, "CYLINDER": 0}
        }
        
        for proxy in proxies:
            ptype = proxy.get("proxy_type", "unknown")
            stats["by_type"][ptype] = stats["by_type"].get(ptype, 0) + 1
            
            shape = self.PROXY_SHAPES.get(ptype, "CUBE")
            stats["by_shape"][shape] += 1
        
        return stats
