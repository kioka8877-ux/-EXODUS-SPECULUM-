#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate LOGISTIQUE - Ghost Detector
Détection des objets Ghost Proxy dans la scène Blender.

Un Ghost Proxy est un objet placeholder avec custom property ghost_proxy=True,
destiné à être remplacé par un asset 3D réel depuis ASSETSHUB.
"""

from dataclasses import dataclass
from typing import List, Tuple, Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


@dataclass
class GhostProxy:
    """
    Représente un objet Ghost Proxy détecté dans la scène.
    
    Attributes:
        name: Nom de l'objet Blender
        proxy_type: Type d'asset (sofa, table, chair, plant, etc.)
        dimensions: Dimensions X, Y, Z en mètres
        location: Position world (X, Y, Z)
        rotation: Rotation Euler (X, Y, Z) en radians
        scale: Facteur d'échelle (X, Y, Z)
        blender_object: Référence directe à l'objet bpy.types.Object
    """
    name: str
    proxy_type: str
    dimensions: Tuple[float, float, float]
    location: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    blender_object: Any

    def __repr__(self) -> str:
        dims = f"{self.dimensions[0]:.2f}x{self.dimensions[1]:.2f}x{self.dimensions[2]:.2f}"
        return f"GhostProxy({self.name}, type={self.proxy_type}, dims={dims}m)"


class GhostDetector:
    """
    Détecte et extrait les Ghost Proxies depuis une scène Blender.
    
    Usage:
        detector = GhostDetector()
        proxies = detector.scan_scene()
        for proxy in proxies:
            print(f"Found: {proxy.name} ({proxy.proxy_type})")
    """
    
    GHOST_PROPERTY = "ghost_proxy"
    TYPE_PROPERTY = "proxy_type"
    DEFAULT_TYPE = "furniture"
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs de détection
        """
        self.verbose = verbose
        self._proxies: List[GhostProxy] = []
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"👻 [GhostDetector] {message}")
    
    def _extract_proxy_type(self, obj: Any) -> str:
        """
        Extrait le type de proxy depuis les custom properties ou le nom.
        
        Priority:
        1. Custom property 'proxy_type'
        2. Parsing du nom (sofa_001 → sofa)
        3. DEFAULT_TYPE fallback
        """
        if obj.get(self.TYPE_PROPERTY):
            return str(obj[self.TYPE_PROPERTY]).lower()
        
        name_lower = obj.name.lower()
        known_types = [
            "sofa", "table", "chair", "plant", "lamp", "shelf",
            "bed", "desk", "cabinet", "rug", "mirror", "tv", "bookcase"
        ]
        
        for ptype in known_types:
            if ptype in name_lower:
                return ptype
        
        return self.DEFAULT_TYPE
    
    def _is_ghost_proxy(self, obj: Any) -> bool:
        """Vérifie si l'objet est un Ghost Proxy."""
        return obj.get(self.GHOST_PROPERTY) == True
    
    def scan_scene(self, collection_filter: Optional[str] = None) -> List[GhostProxy]:
        """
        Scanne la scène pour détecter tous les Ghost Proxies.
        
        Args:
            collection_filter: Nom de collection optionnel pour limiter la recherche
            
        Returns:
            Liste de GhostProxy dataclass
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - scan impossible")
            return []
        
        self._proxies = []
        self._log("Démarrage du scan de scène...")
        
        if collection_filter:
            collection = bpy.data.collections.get(collection_filter)
            if not collection:
                self._log(f"⚠️ Collection '{collection_filter}' non trouvée")
                return []
            objects_to_scan = collection.objects
        else:
            objects_to_scan = bpy.data.objects
        
        for obj in objects_to_scan:
            if self._is_ghost_proxy(obj):
                proxy = self._create_ghost_proxy(obj)
                self._proxies.append(proxy)
                self._log(f"  ✓ Détecté: {proxy}")
        
        self._log(f"Scan terminé: {len(self._proxies)} ghost proxy(s) trouvé(s)")
        return self._proxies
    
    def _create_ghost_proxy(self, obj: Any) -> GhostProxy:
        """Crée un GhostProxy depuis un objet Blender."""
        return GhostProxy(
            name=obj.name,
            proxy_type=self._extract_proxy_type(obj),
            dimensions=(
                obj.dimensions.x,
                obj.dimensions.y,
                obj.dimensions.z
            ),
            location=(
                obj.location.x,
                obj.location.y,
                obj.location.z
            ),
            rotation=(
                obj.rotation_euler.x,
                obj.rotation_euler.y,
                obj.rotation_euler.z
            ),
            scale=(
                obj.scale.x,
                obj.scale.y,
                obj.scale.z
            ),
            blender_object=obj
        )
    
    def scan_by_type(self, proxy_type: str) -> List[GhostProxy]:
        """
        Retourne les proxies d'un type spécifique.
        
        Args:
            proxy_type: Type recherché (sofa, table, etc.)
            
        Returns:
            Liste filtrée de GhostProxy
        """
        if not self._proxies:
            self.scan_scene()
        
        return [p for p in self._proxies if p.proxy_type == proxy_type.lower()]
    
    def get_type_summary(self) -> dict:
        """
        Retourne un résumé des types de proxies détectés.
        
        Returns:
            Dict {type: count}
        """
        if not self._proxies:
            self.scan_scene()
        
        summary = {}
        for proxy in self._proxies:
            summary[proxy.proxy_type] = summary.get(proxy.proxy_type, 0) + 1
        
        return summary
    
    @property
    def proxies(self) -> List[GhostProxy]:
        """Accès direct aux proxies détectés."""
        return self._proxies
    
    @property
    def count(self) -> int:
        """Nombre de proxies détectés."""
        return len(self._proxies)


if __name__ == "__main__":
    print("=" * 50)
    print("GHOST DETECTOR - Test Mode (sans Blender)")
    print("=" * 50)
    
    test_proxy = GhostProxy(
        name="sofa_living_001",
        proxy_type="sofa",
        dimensions=(2.8, 1.5, 0.85),
        location=(3.0, 2.5, 0.0),
        rotation=(0.0, 0.0, 1.57),
        scale=(1.0, 1.0, 1.0),
        blender_object=None
    )
    
    print(f"\n📦 Test GhostProxy dataclass:")
    print(f"   {test_proxy}")
    print(f"   name: {test_proxy.name}")
    print(f"   type: {test_proxy.proxy_type}")
    print(f"   dims: {test_proxy.dimensions}")
    
    detector = GhostDetector(verbose=True)
    print(f"\n✅ GhostDetector initialisé (bpy_available={BPY_AVAILABLE})")
    
    if not BPY_AVAILABLE:
        detector._proxies = [test_proxy]
        summary = detector.get_type_summary()
        print(f"\n📊 Type summary (mock): {summary}")
    
    print("\n✅ Module ghost_detector.py fonctionnel")
