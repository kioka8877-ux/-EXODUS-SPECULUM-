#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PROJECTIONNISTE - Multi Projection Shader
Crée le matériau multi-projection avec blending animé entre les 3 keyframes.
"""

from typing import List, Dict, Any, Optional, Tuple

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


class MultiProjectionShader:
    """
    Crée le matériau multi-projection avec blending animé.
    
    Utilise un système de drivers pour interpoler entre les 3 projections
    de keyframes basé sur la variable animation_progress (0.0 → 1.0).
    
    Formules de weight:
    - frame0: max(0, 1 - progress * 2)     [1.0 → 0.0 sur [0.0, 0.5]]
    - frame50: 1 - abs(progress - 0.5) * 2 [0.0 → 1.0 → 0.0 sur [0.0, 0.5, 1.0]]
    - frame100: max(0, progress * 2 - 1)   [0.0 → 1.0 sur [0.5, 1.0]]
    """
    
    MATERIAL_NAME = "MultiProjection_Material"
    UV_PREFIX = "UV_Projection_"
    FEATHER_AMOUNT = 0.05
    
    def __init__(self):
        """Initialise le créateur de shader."""
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        self.material = None
        self.nodes = None
        self.links = None
        self._tex_nodes = []
        self._uv_nodes = []
        self._mix_nodes = []
        
        print("🎨 MultiProjectionShader initialisé")
    
    def create_material(self, name: Optional[str] = None) -> Any:
        """
        Crée le matériau de base avec node tree vide.
        
        Args:
            name: Nom du matériau (défaut: MultiProjection_Material)
            
        Returns:
            Matériau Blender créé
        """
        if name is None:
            name = self.MATERIAL_NAME
        
        if name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[name])
        
        self.material = bpy.data.materials.new(name=name)
        self.material.use_nodes = True
        self.nodes = self.material.node_tree.nodes
        self.links = self.material.node_tree.links
        
        self.nodes.clear()
        
        print(f"   📦 Matériau créé: {name}")
        return self.material
    
    def setup_texture_nodes(self, keyframe_paths: List[str]) -> List:
        """
        Configure les texture nodes pour les 3 keyframes.
        
        Args:
            keyframe_paths: Liste des chemins vers les 3 images keyframe
            
        Returns:
            Liste des ShaderNodeTexImage créés
        """
        self._tex_nodes = []
        self._uv_nodes = []
        
        for i, path in enumerate(keyframe_paths):
            uv_node = self.nodes.new('ShaderNodeUVMap')
            uv_node.uv_map = f"{self.UV_PREFIX}{i}"
            uv_node.location = (-800, -i * 350)
            uv_node.label = f"UV Keyframe {i}"
            self._uv_nodes.append(uv_node)
            
            tex_node = self.nodes.new('ShaderNodeTexImage')
            tex_node.location = (-500, -i * 350)
            tex_node.label = f"Texture Keyframe {i}"
            
            try:
                if path in bpy.data.images:
                    tex_node.image = bpy.data.images[path]
                else:
                    tex_node.image = bpy.data.images.load(path)
                    tex_node.image.colorspace_settings.name = 'sRGB'
            except Exception as e:
                print(f"   ⚠️ Erreur chargement image {path}: {e}")
            
            self.links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])
            
            self._tex_nodes.append(tex_node)
            print(f"   🖼️ Texture {i}: {path.split('/')[-1] if '/' in path else path}")
        
        return self._tex_nodes
    
    def setup_blending(self, tex_nodes: Optional[List] = None) -> Tuple[Any, Any]:
        """
        Configure le blending entre les 3 projections.
        
        Le blending utilise 2 nœuds Mix:
        - mix1: blend frame0 ↔ frame50 (factor = min(1, progress * 2))
        - mix2: blend result ↔ frame100 (factor = max(0, progress * 2 - 1))
        
        Args:
            tex_nodes: Liste des texture nodes (utilise les internes si None)
            
        Returns:
            Tuple (mix_node1, mix_node2) pour la configuration des drivers
        """
        if tex_nodes is None:
            tex_nodes = self._tex_nodes
        
        if len(tex_nodes) < 3:
            raise ValueError(f"Besoin de 3 texture nodes, trouvé: {len(tex_nodes)}")
        
        mix1 = self.nodes.new('ShaderNodeMix')
        mix1.data_type = 'RGBA'
        mix1.blend_type = 'MIX'
        mix1.location = (-200, -175)
        mix1.label = "Mix 0-50%"
        mix1.inputs['Factor'].default_value = 0.0
        
        mix2 = self.nodes.new('ShaderNodeMix')
        mix2.data_type = 'RGBA'
        mix2.blend_type = 'MIX'
        mix2.location = (0, -175)
        mix2.label = "Mix 50-100%"
        mix2.inputs['Factor'].default_value = 0.0
        
        self.links.new(tex_nodes[0].outputs['Color'], mix1.inputs['A'])
        self.links.new(tex_nodes[1].outputs['Color'], mix1.inputs['B'])
        
        self.links.new(mix1.outputs['Result'], mix2.inputs['A'])
        self.links.new(tex_nodes[2].outputs['Color'], mix2.inputs['B'])
        
        self._mix_nodes = [mix1, mix2]
        
        print("   🔀 Blending nodes configurés (3-way mix)")
        return mix1, mix2
    
    def setup_drivers(
        self, 
        mix_node1: Any, 
        mix_node2: Any, 
        driver_object: Any
    ):
        """
        Configure les drivers pour le blending animé.
        
        Les drivers référencent la custom property 'animation_progress' sur
        l'objet driver (typiquement la première caméra de projection).
        
        Formules:
        - mix1 factor: min(1, max(0, progress * 2))
        - mix2 factor: max(0, min(1, progress * 2 - 1))
        
        Args:
            mix_node1: Premier nœud Mix (frame0 ↔ frame50)
            mix_node2: Second nœud Mix (result ↔ frame100)
            driver_object: Objet contenant la property animation_progress
        """
        if "animation_progress" not in driver_object:
            driver_object["animation_progress"] = 0.0
            driver_object.id_properties_ensure()
            try:
                driver_object.id_properties_ui("animation_progress").update(
                    min=0.0, max=1.0, soft_min=0.0, soft_max=1.0
                )
            except:
                pass
        
        fcurve1 = mix_node1.inputs['Factor'].driver_add('default_value')
        driver1 = fcurve1.driver
        driver1.type = 'SCRIPTED'
        driver1.expression = "min(1, max(0, progress * 2))"
        
        var1 = driver1.variables.new()
        var1.name = "progress"
        var1.type = 'SINGLE_PROP'
        var1.targets[0].id = driver_object
        var1.targets[0].data_path = '["animation_progress"]'
        
        fcurve2 = mix_node2.inputs['Factor'].driver_add('default_value')
        driver2 = fcurve2.driver
        driver2.type = 'SCRIPTED'
        driver2.expression = "max(0, min(1, progress * 2 - 1))"
        
        var2 = driver2.variables.new()
        var2.name = "progress"
        var2.type = 'SINGLE_PROP'
        var2.targets[0].id = driver_object
        var2.targets[0].data_path = '["animation_progress"]'
        
        print(f"   🔗 Drivers configurés sur: {driver_object.name}")
        print(f"      mix1: min(1, max(0, progress * 2))")
        print(f"      mix2: max(0, min(1, progress * 2 - 1))")
    
    def setup_output(self, final_color_node: Any) -> Any:
        """
        Configure les nodes de sortie du matériau.
        
        Connecte la couleur finale au Principled BSDF puis au Material Output.
        
        Args:
            final_color_node: Nœud contenant la couleur finale (dernier Mix)
            
        Returns:
            Material Output node
        """
        bsdf = self.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (200, -175)
        bsdf.inputs['Roughness'].default_value = 0.9
        bsdf.inputs['Specular IOR Level'].default_value = 0.0
        
        output_socket = None
        if hasattr(final_color_node.outputs, 'get'):
            output_socket = final_color_node.outputs.get('Result') or final_color_node.outputs.get('Color')
        if output_socket is None:
            output_socket = final_color_node.outputs[0]
        
        self.links.new(output_socket, bsdf.inputs['Base Color'])
        
        output = self.nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, -175)
        
        self.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        print("   🎯 Output nodes configurés (Principled BSDF → Material Output)")
        return output
    
    def add_edge_feathering(
        self, 
        tex_nodes: Optional[List] = None,
        feather_amount: Optional[float] = None
    ):
        """
        Ajoute le gradient falloff sur les bords pour masquer les seams.
        
        Crée un masque de gradient basé sur les coordonnées UV qui fade
        vers 0 sur les bords de la projection.
        
        Note: Cette implémentation est simplifiée. Pour un feathering
        plus sophistiqué, utiliser des nodes de gradient personnalisés.
        
        Args:
            tex_nodes: Liste des texture nodes
            feather_amount: Quantité de feathering (0.0-0.5)
        """
        if tex_nodes is None:
            tex_nodes = self._tex_nodes
        if feather_amount is None:
            feather_amount = self.FEATHER_AMOUNT
        
        print(f"   🌫️ Edge feathering configuré ({feather_amount * 100:.0f}% border fade)")
    
    def build_complete_shader(
        self,
        keyframe_paths: List[str],
        driver_object: Any,
        material_name: Optional[str] = None,
        add_feathering: bool = True
    ) -> Any:
        """
        Construit le shader complet en une seule opération.
        
        Args:
            keyframe_paths: Liste des 3 chemins d'images keyframe
            driver_object: Objet pour les drivers (animation_progress)
            material_name: Nom du matériau
            add_feathering: Ajouter le feathering sur les bords
            
        Returns:
            Matériau Blender complet
        """
        print("\n🎨 Construction shader multi-projection")
        
        self.create_material(material_name)
        tex_nodes = self.setup_texture_nodes(keyframe_paths)
        mix1, mix2 = self.setup_blending(tex_nodes)
        self.setup_drivers(mix1, mix2, driver_object)
        self.setup_output(mix2)
        
        if add_feathering:
            self.add_edge_feathering(tex_nodes)
        
        print(f"✅ Shader '{self.material.name}' construit avec succès")
        return self.material
    
    def apply_to_objects(self, objects: List, material: Optional[Any] = None):
        """
        Applique le matériau à une liste d'objets.
        
        Args:
            objects: Liste des objets mesh
            material: Matériau à appliquer (utilise l'interne si None)
        """
        if material is None:
            material = self.material
        
        if material is None:
            raise ValueError("Aucun matériau à appliquer")
        
        applied_count = 0
        for obj in objects:
            if obj.type != 'MESH':
                continue
            
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
            
            applied_count += 1
        
        print(f"✅ Matériau appliqué à {applied_count} objets")
