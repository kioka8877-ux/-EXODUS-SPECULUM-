#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate CORTEX - Analyseur de Pièces
Extraction des dimensions, matériaux et meubles via Gemini.
"""

from typing import Dict, Any, List
from pathlib import Path

from .gemini_client import GeminiClient


ROOM_ANALYSIS_PROMPT = """
Analyse cette image d'intérieur immobilier et retourne un JSON avec:

{
    "room_type": "living_room|bedroom|kitchen|bathroom|office|dining_room|hallway|other",
    "estimated_dimensions": {
        "width_meters": float,
        "length_meters": float,
        "height_meters": float,
        "confidence": "high|medium|low"
    },
    "materials": [
        {
            "type": "marble|wood|tile|carpet|concrete|fabric|glass|metal",
            "location": "floor|wall|ceiling|furniture",
            "color": "string",
            "finish": "matte|glossy|textured"
        }
    ],
    "furniture": [
        {
            "type": "sofa|chair|table|bed|cabinet|lamp|plant|tv|mirror|other",
            "position": {"x_percent": 0-100, "y_percent": 0-100},
            "size": "small|medium|large",
            "color": "string"
        }
    ],
    "lighting": {
        "mood": "warm|cold|neutral|dramatic",
        "sources": ["natural|artificial|mixed"],
        "brightness": "bright|moderate|dim"
    },
    "style": "modern|classic|minimalist|industrial|scandinavian|luxury|other"
}

Sois précis et utilise uniquement les valeurs proposées. Retourne UNIQUEMENT le JSON, pas d'explication.
"""

DIMENSIONS_PROMPT = """
En regardant cette pièce, estime les dimensions en mètres.
Utilise les meubles standard comme référence (canapé ~2m, porte ~2m hauteur, etc.).

Retourne UNIQUEMENT ce JSON:
{
    "width_meters": float,
    "length_meters": float, 
    "height_meters": float,
    "reference_objects": ["liste des objets utilisés comme référence"],
    "confidence": "high|medium|low"
}
"""

MATERIALS_PROMPT = """
Identifie tous les matériaux visibles dans cette image d'intérieur.

Retourne UNIQUEMENT ce JSON:
{
    "materials": [
        {
            "type": "marble|wood|tile|carpet|concrete|fabric|glass|metal|stone|leather|velvet",
            "location": "floor|wall|ceiling|furniture|window|door",
            "color": "descriptif couleur",
            "coverage_percent": 0-100
        }
    ]
}
"""


class RoomAnalyzer:
    """
    Analyseur de pièces via Gemini.
    Extrait dimensions, matériaux, meubles et style.
    """
    
    def __init__(self, gemini_client: GeminiClient = None):
        """
        Args:
            gemini_client: Client Gemini (créé si non fourni)
        """
        self.client = gemini_client or GeminiClient()
    
    def analyze_room(self, image_path: str) -> Dict[str, Any]:
        """
        Analyse complète d'une pièce.
        
        Args:
            image_path: Chemin de l'image
            
        Returns:
            Dict avec toutes les analyses
        """
        print(f"🔍 Analyse pièce: {Path(image_path).name}")
        
        result = self.client.analyze_image(image_path, ROOM_ANALYSIS_PROMPT)
        
        if result["status"] == "success" and result["data"]:
            print(f"   ✅ Type: {result['data'].get('room_type', 'unknown')}")
            print(f"   ✅ Style: {result['data'].get('style', 'unknown')}")
            return result["data"]
        else:
            print(f"   ⚠️ Analyse échouée: {result.get('error', 'No data')}")
            return {"error": result.get("error"), "raw": result.get("raw_response")}
    
    def estimate_dimensions(self, image_path: str) -> Dict[str, Any]:
        """Estime les dimensions de la pièce."""
        result = self.client.analyze_image(image_path, DIMENSIONS_PROMPT)
        return result.get("data", {})
    
    def detect_materials(self, image_path: str) -> Dict[str, Any]:
        """Détecte les matériaux présents."""
        result = self.client.analyze_image(image_path, MATERIALS_PROMPT)
        return result.get("data", {})
    
    def analyze_keyframes(self, 
                          keyframe_paths: List[str],
                          merge_results: bool = True) -> Dict[str, Any]:
        """
        Analyse plusieurs keyframes et fusionne les résultats.
        
        Args:
            keyframe_paths: Liste des chemins (typiquement 3: début, milieu, fin)
            merge_results: Fusionner les analyses
            
        Returns:
            Dict avec analyse fusionnée ou liste d'analyses
        """
        print(f"🔍 Analyse de {len(keyframe_paths)} keyframes...")
        
        analyses = []
        for i, path in enumerate(keyframe_paths):
            print(f"   [{i+1}/{len(keyframe_paths)}] {Path(path).name}")
            analysis = self.analyze_room(path)
            analyses.append({
                "frame": path,
                "analysis": analysis
            })
        
        if not merge_results:
            return {"keyframes": analyses}
        
        merged = self._merge_analyses(analyses)
        return merged
    
    def _merge_analyses(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Fusionne plusieurs analyses en une seule."""
        if not analyses:
            return {}
        
        base = analyses[0]["analysis"]
        if not isinstance(base, dict) or "error" in base:
            return {"error": "Analysis failed", "raw_analyses": analyses}
        
        all_furniture = []
        all_materials = []
        
        for a in analyses:
            data = a.get("analysis", {})
            if isinstance(data, dict):
                all_furniture.extend(data.get("furniture", []))
                all_materials.extend(data.get("materials", []))
        
        seen_furniture = set()
        unique_furniture = []
        for f in all_furniture:
            key = f.get("type", "") + str(f.get("position", {}))
            if key not in seen_furniture:
                seen_furniture.add(key)
                unique_furniture.append(f)
        
        merged = {
            "room_type": base.get("room_type"),
            "estimated_dimensions": base.get("estimated_dimensions"),
            "materials": all_materials[:10],
            "furniture": unique_furniture,
            "lighting": base.get("lighting"),
            "style": base.get("style"),
            "keyframes_analyzed": len(analyses)
        }
        
        return merged
