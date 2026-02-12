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

IMPORTANT pour les dimensions:
- Un canapé standard fait ~2m de long
- Une porte standard fait ~2m de haut et ~0.9m de large
- Un lit double fait ~1.6m x 2m
- Utilise ces références pour estimer les dimensions RÉALISTES de la pièce
- Une pièce de salon typique fait 4-6m de large, pas 10-15m

{
    "room_type": "living_room|bedroom|kitchen|bathroom|office|dining_room|hallway|other",
    "estimated_dimensions": {
        "width_meters": float (utiliser meubles comme référence, typiquement 3-8m),
        "length_meters": float (utiliser meubles comme référence, typiquement 3-10m),
        "height_meters": float (typiquement 2.5-3.5m),
        "reference_objects": ["liste des objets utilisés pour calibrer"],
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

UNIFIED_ANALYSIS_PROMPT = """
Tu reçois 3 images d'une même pièce immobilière (début, milieu, fin d'une vidéo walkthrough).
Analyse-les ENSEMBLE et retourne un JSON unique combinant l'analyse de la pièce ET les points d'intérêt.

IMPORTANT pour les dimensions:
- Un canapé standard fait ~2m de long
- Une porte standard fait ~2m de haut et ~0.9m de large
- Un lit double fait ~1.6m x 2m
- Utilise ces références pour estimer les dimensions RÉALISTES de la pièce
- Une pièce de salon typique fait 4-6m de large, pas 10-15m

Retourne UNIQUEMENT ce JSON:
{
    "room_analysis": {
        "room_type": "living_room|bedroom|kitchen|bathroom|office|dining_room|hallway|other",
        "estimated_dimensions": {
            "width_meters": float,
            "length_meters": float,
            "height_meters": float,
            "reference_objects": ["liste des objets utilisés pour calibrer"],
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
    },
    "points_of_interest": {
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
}

Analyse les 3 images ensemble pour une vue complète. Utilise l'image centrale (2ème) comme référence principale pour les POI.
Sois précis et utilise uniquement les valeurs proposées. Retourne UNIQUEMENT le JSON.
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
    
    def analyze_all_in_one(self, 
                           keyframe_paths: List[str],
                           central_index: int = 1) -> tuple:
        """
        Analyse combinée room + POI en un seul appel multi-image.
        Optimisation PHÉNIX-SOUVERAIN: 4 appels → 1.
        
        Args:
            keyframe_paths: Liste des chemins keyframes (typiquement 3)
            central_index: Index du frame central pour POI (défaut: 1 = milieu)
            
        Returns:
            Tuple (room_data: Dict, poi_data: Dict)
        """
        print(f"🔍 Analyse unifiée de {len(keyframe_paths)} keyframes (single-call)...")
        for i, path in enumerate(keyframe_paths):
            print(f"   [{i+1}/{len(keyframe_paths)}] {Path(path).name}")
        
        result = self.client.analyze_multiple_images(
            keyframe_paths, 
            UNIFIED_ANALYSIS_PROMPT
        )
        
        if result["status"] == "success" and result["data"]:
            data = result["data"]
            
            room_data = data.get("room_analysis", {})
            if not room_data:
                room_data = {
                    "room_type": data.get("room_type"),
                    "estimated_dimensions": data.get("estimated_dimensions"),
                    "materials": data.get("materials", []),
                    "furniture": data.get("furniture", []),
                    "lighting": data.get("lighting"),
                    "style": data.get("style")
                }
            
            poi_data = data.get("points_of_interest", {})
            if not poi_data:
                poi_data = {
                    "points_of_interest": [],
                    "primary_focal_point": {"x_percent": 50, "y_percent": 50},
                    "composition_notes": ""
                }
            
            room_data["keyframes_analyzed"] = len(keyframe_paths)
            
            print(f"   ✅ Type: {room_data.get('room_type', 'unknown')}")
            print(f"   ✅ Style: {room_data.get('style', 'unknown')}")
            print(f"   ✅ POI: {len(poi_data.get('points_of_interest', []))} détectés")
            
            return room_data, poi_data
        else:
            error = result.get("error", "No data")
            print(f"   ⚠️ Analyse unifiée échouée: {error}")
            
            room_data = {
                "room_type": "other",
                "estimated_dimensions": {
                    "width_meters": 5.0,
                    "length_meters": 6.0,
                    "height_meters": 2.8,
                    "reference_objects": [],
                    "confidence": "low"
                },
                "materials": [],
                "furniture": [],
                "lighting": {"mood": "neutral", "sources": ["natural"], "brightness": "moderate"},
                "style": "modern",
                "keyframes_analyzed": len(keyframe_paths),
                "error": error
            }
            poi_data = {
                "points_of_interest": [],
                "primary_focal_point": {"x_percent": 50, "y_percent": 50},
                "composition_notes": ""
            }
            return room_data, poi_data
    
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
