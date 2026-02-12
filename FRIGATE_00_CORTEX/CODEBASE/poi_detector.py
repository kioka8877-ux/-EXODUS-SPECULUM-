#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate CORTEX - Détecteur de Points d'Intérêt
Génère une heatmap des zones importantes pour le Smart-Crop.

Note PHÉNIX-SOUVERAIN: La détection POI est désormais intégrée dans
l'appel unifié de RoomAnalyzer.analyze_all_in_one(). La méthode
detect_poi() reste disponible pour usage standalone.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from pathlib import Path

from .gemini_client import GeminiClient


POI_PROMPT = """
Identifie les Points d'Intérêt (POI) dans cette image d'intérieur.
Les POI sont les éléments sur lesquels un spectateur porterait son attention.

Retourne UNIQUEMENT ce JSON:
{
    "points_of_interest": [
        {
            "type": "furniture|window|artwork|architectural|focal_point",
            "description": "courte description",
            "position": {
                "x_percent": 0-100,
                "y_percent": 0-100
            },
            "importance": 1-10,
            "size_percent": 0-100
        }
    ],
    "primary_focal_point": {
        "x_percent": 0-100,
        "y_percent": 0-100
    },
    "composition_notes": "string"
}
"""


class POIDetector:
    """
    Détecteur de Points d'Intérêt pour le Smart-Crop.
    Génère une heatmap 32x32 des zones importantes.
    """
    
    HEATMAP_SIZE = 32
    
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or GeminiClient()
    
    def detect_poi(self, image_path: str) -> Dict[str, Any]:
        """
        Détecte les POI dans une image.
        
        Returns:
            Dict avec POI et focal point
        """
        result = self.client.analyze_image(image_path, POI_PROMPT)
        data = result.get("data")
        if data is None:
            return {"points_of_interest": [], "primary_focal_point": None, "error": result.get("error")}
        return data
    
    def generate_heatmap(self, 
                         poi_data: Dict[str, Any],
                         size: int = None) -> np.ndarray:
        """
        Génère une heatmap numpy à partir des POI.
        
        Args:
            poi_data: Données POI de detect_poi()
            size: Taille de la grille (défaut: 32x32)
            
        Returns:
            numpy array (size, size) avec valeurs 0-1
        """
        size = size or self.HEATMAP_SIZE
        heatmap = np.zeros((size, size), dtype=np.float32)
        
        pois = poi_data.get("points_of_interest", [])
        
        for poi in pois:
            pos = poi.get("position", {})
            x_pct = pos.get("x_percent", 50)
            y_pct = pos.get("y_percent", 50)
            importance = poi.get("importance", 5) / 10.0
            size_pct = poi.get("size_percent", 10) / 100.0
            
            x = int(x_pct / 100 * size)
            y = int(y_pct / 100 * size)
            radius = max(1, int(size_pct * size / 2))
            
            self._add_gaussian_blob(heatmap, x, y, radius, importance)
        
        focal = poi_data.get("primary_focal_point", {})
        if focal:
            fx = int(focal.get("x_percent", 50) / 100 * size)
            fy = int(focal.get("y_percent", 50) / 100 * size)
            self._add_gaussian_blob(heatmap, fx, fy, size // 4, 0.5)
        
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap
    
    def _add_gaussian_blob(self, 
                           heatmap: np.ndarray,
                           cx: int, cy: int,
                           radius: int,
                           intensity: float):
        """Ajoute un blob gaussien à la heatmap."""
        size = heatmap.shape[0]
        
        for y in range(max(0, cy - radius), min(size, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(size, cx + radius + 1)):
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist <= radius:
                    value = intensity * np.exp(-(dist**2) / (2 * (radius/2)**2))
                    heatmap[y, x] = max(heatmap[y, x], value)
    
    def get_crop_center(self, heatmap: np.ndarray) -> Tuple[float, float]:
        """
        Calcule le centre optimal pour le crop basé sur la heatmap.
        
        Returns:
            (x_percent, y_percent) du centre optimal
        """
        size = heatmap.shape[0]
        total = heatmap.sum()
        
        if total == 0:
            return (50.0, 50.0)
        
        y_indices, x_indices = np.mgrid[0:size, 0:size]
        
        cx = (x_indices * heatmap).sum() / total
        cy = (y_indices * heatmap).sum() / total
        
        x_pct = (cx / size) * 100
        y_pct = (cy / size) * 100
        
        return (x_pct, y_pct)
