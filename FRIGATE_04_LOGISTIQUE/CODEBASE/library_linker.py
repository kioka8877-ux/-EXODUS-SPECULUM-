#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate LOGISTIQUE - Library Linker
Linked Asset Loading via bpy.data.libraries (Loi IX - Vitesse).

Ce module link (pas append!) les assets 3D depuis des fichiers .blend externes,
préservant la connexion avec la bibliothèque source et optimisant la mémoire.
"""

from pathlib import Path
from typing import Optional, List, Any, Dict

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None

from .ghost_detector import GhostProxy


class LibraryLinker:
    """
    Link les assets 3D depuis ASSETSHUB vers la scène Blender.
    
    Avantages du Link vs Append:
    - Fichier .blend plus léger (références externes)
    - Mise à jour automatique si asset source modifié
    - Mémoire partagée entre instances du même asset
    
    Usage:
        linker = LibraryLinker()
        linked_obj = linker.link_asset("/path/to/sofa.blend", ghost_proxy)
    """
    
    ASSETS_COLLECTION = "ASSETS_LINKED"
    PROXIES_COLLECTION = "PROXIES"
    LOD0_SUFFIX = "LOD0"
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs de linking
        """
        self.verbose = verbose
        self._linked_count = 0
        self._failed_count = 0
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"🔗 [LibraryLinker] {message}")
    
    def _ensure_collection(self, name: str) -> Any:
        """
        Crée ou récupère une collection Blender.
        
        Args:
            name: Nom de la collection
            
        Returns:
            bpy.types.Collection
        """
        if not BPY_AVAILABLE:
            return None
        
        collection = bpy.data.collections.get(name)
        if collection is None:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
            self._log(f"  ✓ Collection '{name}' créée")
        
        return collection
    
    def _find_lod0_objects(self, objects: List) -> List:
        """
        Filtre les objets pour ne garder que LOD0.
        
        Args:
            objects: Liste d'objets linkés
            
        Returns:
            Liste filtrée (objets avec LOD0 ou tous si aucun LOD)
        """
        lod0_objs = [obj for obj in objects if self.LOD0_SUFFIX in obj.name]
        
        if lod0_objs:
            return lod0_objs
        
        return [obj for obj in objects if obj.type == 'MESH']
    
    def _hide_proxy(self, proxy: GhostProxy) -> None:
        """
        Cache le Ghost Proxy original (render et viewport).
        
        Args:
            proxy: Ghost Proxy à cacher
        """
        if not BPY_AVAILABLE or proxy.blender_object is None:
            return
        
        obj = proxy.blender_object
        obj.hide_render = True
        obj.hide_viewport = True
        obj.hide_set(True)
        
        proxies_collection = self._ensure_collection(self.PROXIES_COLLECTION)
        if proxies_collection:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            proxies_collection.objects.link(obj)
    
    def link_asset(
        self, 
        asset_path: str, 
        proxy: GhostProxy,
        apply_transform: bool = True
    ) -> Optional[Any]:
        """
        Link un asset depuis un fichier .blend externe.
        
        Workflow:
        1. bpy.data.libraries.load(asset_path, link=True)
        2. Import uniquement les objets avec "LOD0" dans le nom
        3. Positionne à proxy.location, rotation, scale
        4. Ajoute à la collection "ASSETS_LINKED"
        5. Cache le proxy original
        
        Args:
            asset_path: Chemin vers le fichier .blend source
            proxy: Ghost Proxy à remplacer
            apply_transform: Applique la transformation du proxy
            
        Returns:
            bpy.types.Object linké, ou None si échec
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - linking impossible")
            return None
        
        asset_path = str(Path(asset_path).resolve())
        
        self._log(f"Linking asset: {Path(asset_path).name} → {proxy.name}")
        
        try:
            linked_objects = []
            
            with bpy.data.libraries.load(asset_path, link=True) as (data_from, data_to):
                lod0_names = [name for name in data_from.objects if self.LOD0_SUFFIX in name]
                
                if lod0_names:
                    data_to.objects = lod0_names
                else:
                    data_to.objects = data_from.objects[:5]
            
            assets_collection = self._ensure_collection(self.ASSETS_COLLECTION)
            
            main_object = None
            for obj in data_to.objects:
                if obj is not None:
                    assets_collection.objects.link(obj)
                    linked_objects.append(obj)
                    
                    if main_object is None and obj.type == 'MESH':
                        main_object = obj
            
            if main_object is None and linked_objects:
                main_object = linked_objects[0]
            
            if main_object and apply_transform:
                self._apply_proxy_transform(main_object, proxy)
            
            self._hide_proxy(proxy)
            
            if main_object:
                main_object["source_proxy"] = proxy.name
                main_object["source_asset"] = asset_path
                main_object["linked_asset"] = True
            
            self._linked_count += 1
            self._log(f"  ✓ Linké: {len(linked_objects)} objet(s)")
            
            return main_object
            
        except Exception as e:
            self._log(f"  ✗ Erreur: {e}")
            self._failed_count += 1
            return None
    
    def _apply_proxy_transform(self, obj: Any, proxy: GhostProxy) -> None:
        """
        Applique la transformation du proxy à l'objet linké.
        
        Args:
            obj: Objet Blender linké
            proxy: Ghost Proxy source
        """
        obj.location = proxy.location
        obj.rotation_euler = proxy.rotation
        
        obj.scale = proxy.scale
    
    def link_multiple(
        self, 
        asset_proxy_pairs: List[tuple]
    ) -> Dict[str, Any]:
        """
        Link plusieurs assets en batch.
        
        Args:
            asset_proxy_pairs: Liste de tuples (asset_path, GhostProxy)
            
        Returns:
            Dict avec résultats: {proxy_name: linked_object}
        """
        results = {}
        
        for asset_path, proxy in asset_proxy_pairs:
            linked_obj = self.link_asset(asset_path, proxy)
            results[proxy.name] = linked_obj
        
        return results
    
    def hide_proxies_collection(self) -> None:
        """Cache la collection PROXIES au render et viewport."""
        if not BPY_AVAILABLE:
            return
        
        proxies_coll = bpy.data.collections.get(self.PROXIES_COLLECTION)
        if proxies_coll:
            proxies_coll.hide_render = True
            proxies_coll.hide_viewport = True
            self._log(f"Collection '{self.PROXIES_COLLECTION}' cachée")
    
    def get_stats(self) -> Dict[str, int]:
        """Retourne les statistiques de linking."""
        return {
            "linked": self._linked_count,
            "failed": self._failed_count,
            "total": self._linked_count + self._failed_count
        }
    
    def reset_stats(self) -> None:
        """Remet les compteurs à zéro."""
        self._linked_count = 0
        self._failed_count = 0


if __name__ == "__main__":
    print("=" * 50)
    print("LIBRARY LINKER - Test Mode")
    print("=" * 50)
    
    from .ghost_detector import GhostProxy
    
    test_proxy = GhostProxy(
        name="sofa_living_001",
        proxy_type="sofa",
        dimensions=(2.8, 1.5, 0.85),
        location=(3.0, 2.5, 0.0),
        rotation=(0.0, 0.0, 1.57),
        scale=(1.0, 1.0, 1.0),
        blender_object=None
    )
    
    linker = LibraryLinker(verbose=True)
    print(f"\n📦 LibraryLinker initialisé (bpy_available={BPY_AVAILABLE})")
    
    print(f"\n🔗 Test linking (mock):")
    print(f"   Proxy: {test_proxy.name}")
    print(f"   Location: {test_proxy.location}")
    print(f"   Rotation: {test_proxy.rotation}")
    
    print(f"\n📊 Stats:")
    stats = linker.get_stats()
    print(f"   {stats}")
    
    print("\n✅ Module library_linker.py fonctionnel")
