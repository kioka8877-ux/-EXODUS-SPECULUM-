#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate LOGISTIQUE - Asset Matcher
Fuzzy Matching pour trouver le meilleur asset 3D correspondant à un Ghost Proxy.

Algorithme de scoring:
    Score = (type_match * 0.4) + (dimension_similarity * 0.6)
    
    dimension_similarity = 1 - (|proxy_dims - asset_dims| / max_dims)
"""

import os
import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .ghost_detector import GhostProxy


@dataclass
class AssetMatch:
    """
    Représente un asset 3D trouvé qui correspond à un Ghost Proxy.
    
    Attributes:
        asset_path: Chemin complet vers le fichier .blend
        asset_type: Type d'asset (sofa, table, chair, etc.)
        dimensions: Dimensions X, Y, Z en mètres
        score: Score de correspondance (0.0 à 1.0)
        metadata: Métadonnées additionnelles (optionnel)
    """
    asset_path: str
    asset_type: str
    dimensions: Tuple[float, float, float]
    score: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __repr__(self) -> str:
        dims = f"{self.dimensions[0]:.2f}x{self.dimensions[1]:.2f}x{self.dimensions[2]:.2f}"
        return f"AssetMatch({Path(self.asset_path).stem}, score={self.score:.2f}, dims={dims}m)"


class AssetMatcher:
    """
    Trouve le meilleur asset 3D depuis ASSETSHUB pour un Ghost Proxy.
    
    Structure ASSETSHUB attendue:
        ASSETSHUB_PATH/
        ├── sofas/
        │   ├── modern_grey_280x150x85.blend
        │   └── sectional_l_300x200x90.blend
        ├── tables/
        │   ├── coffee_oak_120x60x45.blend
        │   └── dining_180x90x75.blend
        ├── chairs/
        └── plants/
    
    Usage:
        matcher = AssetMatcher("/path/to/assetshub")
        match = matcher.find_best_asset(ghost_proxy, threshold=0.7)
        if match:
            print(f"Best match: {match.asset_path}")
    """
    
    TYPE_WEIGHT = 0.4
    DIMENSION_WEIGHT = 0.6
    
    DIMENSION_PATTERN = re.compile(r'(\d+)x(\d+)x(\d+)')
    
    TYPE_FOLDERS = {
        "sofa": "sofas",
        "couch": "sofas",
        "table": "tables",
        "desk": "tables",
        "chair": "chairs",
        "stool": "chairs",
        "plant": "plants",
        "tree": "plants",
        "lamp": "lamps",
        "light": "lamps",
        "shelf": "shelves",
        "bookcase": "shelves",
        "bed": "beds",
        "cabinet": "cabinets",
        "wardrobe": "cabinets",
        "rug": "rugs",
        "carpet": "rugs",
        "mirror": "mirrors",
        "tv": "electronics",
        "furniture": "misc",
    }
    
    def __init__(self, assetshub_path: str, verbose: bool = True):
        """
        Args:
            assetshub_path: Chemin racine vers ASSETSHUB
            verbose: Affiche les logs de matching
        """
        self.assetshub_path = Path(assetshub_path)
        self.verbose = verbose
        self._asset_cache: Dict[str, List[Dict]] = {}
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"🔍 [AssetMatcher] {message}")
    
    def _parse_dimensions_from_filename(self, filename: str) -> Optional[Tuple[float, float, float]]:
        """
        Parse les dimensions depuis le nom de fichier.
        Format attendu: *_WxDxH.blend (dimensions en cm)
        
        Args:
            filename: Nom du fichier (ex: modern_grey_280x150x85.blend)
            
        Returns:
            Tuple (width, depth, height) en mètres, ou None
        """
        match = self.DIMENSION_PATTERN.search(filename)
        if match:
            w_cm, d_cm, h_cm = map(int, match.groups())
            return (w_cm / 100.0, d_cm / 100.0, h_cm / 100.0)
        return None
    
    def _load_metadata(self, blend_path: Path) -> Optional[Dict[str, Any]]:
        """
        Charge les métadonnées JSON associées à un .blend.
        
        Args:
            blend_path: Chemin vers le fichier .blend
            
        Returns:
            Dict de métadonnées ou None
        """
        json_path = blend_path.with_suffix('.json')
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def _get_folder_for_type(self, proxy_type: str) -> str:
        """Retourne le nom du dossier pour un type de proxy."""
        return self.TYPE_FOLDERS.get(proxy_type.lower(), "misc")
    
    def _scan_folder(self, folder_path: Path) -> List[Dict]:
        """
        Scanne un dossier pour trouver tous les assets .blend.
        
        Returns:
            Liste de dicts avec path, dimensions, metadata
        """
        assets = []
        
        if not folder_path.exists():
            return assets
        
        for blend_file in folder_path.glob("*.blend"):
            asset_info = {
                "path": str(blend_file),
                "name": blend_file.stem,
            }
            
            dims = self._parse_dimensions_from_filename(blend_file.name)
            if dims:
                asset_info["dimensions"] = dims
            else:
                asset_info["dimensions"] = (1.0, 1.0, 1.0)
            
            metadata = self._load_metadata(blend_file)
            if metadata:
                asset_info["metadata"] = metadata
                if "dimensions" in metadata:
                    asset_info["dimensions"] = tuple(metadata["dimensions"])
            
            assets.append(asset_info)
        
        return assets
    
    def _calculate_dimension_similarity(
        self, 
        proxy_dims: Tuple[float, float, float],
        asset_dims: Tuple[float, float, float]
    ) -> float:
        """
        Calcule la similarité dimensionnelle entre proxy et asset.
        
        Formula: 1 - (|proxy_dims - asset_dims| / max_dims)
        
        Returns:
            Score entre 0.0 et 1.0
        """
        diff_x = abs(proxy_dims[0] - asset_dims[0])
        diff_y = abs(proxy_dims[1] - asset_dims[1])
        diff_z = abs(proxy_dims[2] - asset_dims[2])
        
        max_x = max(proxy_dims[0], asset_dims[0], 0.01)
        max_y = max(proxy_dims[1], asset_dims[1], 0.01)
        max_z = max(proxy_dims[2], asset_dims[2], 0.01)
        
        sim_x = 1 - (diff_x / max_x)
        sim_y = 1 - (diff_y / max_y)
        sim_z = 1 - (diff_z / max_z)
        
        return max(0.0, (sim_x + sim_y + sim_z) / 3)
    
    def _calculate_type_match(self, proxy_type: str, asset_folder: str) -> float:
        """
        Calcule le score de correspondance de type.
        
        Returns:
            1.0 si type match exact, 0.5 si catégorie similaire, 0.0 sinon
        """
        expected_folder = self._get_folder_for_type(proxy_type)
        
        if asset_folder.lower() == expected_folder.lower():
            return 1.0
        
        similar_categories = {
            "sofas": ["chairs"],
            "tables": ["desks"],
            "chairs": ["sofas", "stools"],
            "lamps": ["electronics"],
        }
        
        similar = similar_categories.get(expected_folder, [])
        if asset_folder.lower() in [s.lower() for s in similar]:
            return 0.5
        
        return 0.0
    
    def find_best_asset(
        self, 
        proxy: GhostProxy, 
        threshold: float = 0.7
    ) -> Optional[AssetMatch]:
        """
        Cherche le meilleur asset correspondant au Ghost Proxy.
        
        Score = (type_match * 0.4) + (dimension_similarity * 0.6)
        
        Args:
            proxy: Le Ghost Proxy à matcher
            threshold: Score minimum requis (0.0 à 1.0)
            
        Returns:
            AssetMatch si trouvé avec score >= threshold, None sinon
        """
        self._log(f"Recherche asset pour: {proxy.name} ({proxy.proxy_type})")
        
        primary_folder = self._get_folder_for_type(proxy.proxy_type)
        search_folders = [primary_folder, "misc"]
        
        best_match: Optional[AssetMatch] = None
        best_score = 0.0
        
        for folder_name in search_folders:
            folder_path = self.assetshub_path / folder_name
            
            if folder_name not in self._asset_cache:
                self._asset_cache[folder_name] = self._scan_folder(folder_path)
            
            assets = self._asset_cache[folder_name]
            
            for asset in assets:
                type_score = self._calculate_type_match(proxy.proxy_type, folder_name)
                dim_score = self._calculate_dimension_similarity(
                    proxy.dimensions,
                    asset["dimensions"]
                )
                
                total_score = (type_score * self.TYPE_WEIGHT) + (dim_score * self.DIMENSION_WEIGHT)
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = AssetMatch(
                        asset_path=asset["path"],
                        asset_type=folder_name.rstrip('s'),
                        dimensions=asset["dimensions"],
                        score=total_score,
                        metadata=asset.get("metadata")
                    )
        
        if best_match and best_match.score >= threshold:
            self._log(f"  ✓ Trouvé: {best_match}")
            return best_match
        
        self._log(f"  ✗ Aucun match trouvé (best_score={best_score:.2f}, threshold={threshold})")
        return None
    
    def find_all_matches(
        self, 
        proxy: GhostProxy, 
        threshold: float = 0.5,
        max_results: int = 5
    ) -> List[AssetMatch]:
        """
        Retourne tous les assets correspondants au-dessus du seuil.
        
        Args:
            proxy: Le Ghost Proxy à matcher
            threshold: Score minimum
            max_results: Nombre max de résultats
            
        Returns:
            Liste d'AssetMatch triée par score décroissant
        """
        matches = []
        
        for folder_path in self.assetshub_path.iterdir():
            if not folder_path.is_dir():
                continue
            
            folder_name = folder_path.name
            
            if folder_name not in self._asset_cache:
                self._asset_cache[folder_name] = self._scan_folder(folder_path)
            
            for asset in self._asset_cache[folder_name]:
                type_score = self._calculate_type_match(proxy.proxy_type, folder_name)
                dim_score = self._calculate_dimension_similarity(
                    proxy.dimensions,
                    asset["dimensions"]
                )
                
                total_score = (type_score * self.TYPE_WEIGHT) + (dim_score * self.DIMENSION_WEIGHT)
                
                if total_score >= threshold:
                    matches.append(AssetMatch(
                        asset_path=asset["path"],
                        asset_type=folder_name.rstrip('s'),
                        dimensions=asset["dimensions"],
                        score=total_score,
                        metadata=asset.get("metadata")
                    ))
        
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:max_results]
    
    def clear_cache(self) -> None:
        """Vide le cache d'assets."""
        self._asset_cache.clear()


if __name__ == "__main__":
    print("=" * 50)
    print("ASSET MATCHER - Test Mode")
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
    
    print(f"\n📦 Test Proxy: {test_proxy}")
    
    matcher = AssetMatcher("/fake/assetshub", verbose=True)
    
    print(f"\n🔍 Test parsing dimensions:")
    test_files = [
        "modern_grey_280x150x85.blend",
        "sectional_300x200x90.blend",
        "no_dims_table.blend"
    ]
    for f in test_files:
        dims = matcher._parse_dimensions_from_filename(f)
        print(f"   {f} → {dims}")
    
    print(f"\n📐 Test dimension similarity:")
    dims_a = (2.8, 1.5, 0.85)
    dims_b = (2.5, 1.4, 0.80)
    sim = matcher._calculate_dimension_similarity(dims_a, dims_b)
    print(f"   {dims_a} vs {dims_b} → similarity={sim:.3f}")
    
    print(f"\n🏷️ Test type matching:")
    types = ["sofa", "table", "plant", "unknown"]
    for t in types:
        folder = matcher._get_folder_for_type(t)
        print(f"   {t} → {folder}")
    
    print("\n✅ Module asset_matcher.py fonctionnel")
