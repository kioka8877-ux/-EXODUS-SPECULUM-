#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate CORTEX - Pipeline Complet
Orchestre l'analyse IA et génère le masterplan.json.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from CORE_CONFIG.paths import F00_INPUT, F00_OUTPUT

from .gemini_client import GeminiClient
from .room_analyzer import RoomAnalyzer
from .poi_detector import POIDetector


class CortexPipeline:
    """
    Pipeline complet de la Frégate CORTEX.
    
    Workflow:
    1. Sélection des keyframes
    2. Analyse des pièces (dimensions, matériaux, meubles)
    3. Détection des POI
    4. Génération du masterplan.json
    """
    
    def __init__(self, project_id: str):
        """
        Args:
            project_id: Identifiant unique du projet
        """
        self.project_id = project_id
        self.input_dir = Path(F00_INPUT) / project_id
        self.output_dir = Path(F00_OUTPUT) / project_id
        
        self.client = None
        self.room_analyzer = None
        self.poi_detector = None
        
        print("🧠 Cortex Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Input: {self.input_dir}")
        print(f"   Output: {self.output_dir}")
    
    def _init_clients(self):
        """Initialise les clients Gemini (lazy loading)."""
        if self.client is None:
            self.client = GeminiClient()
            self.room_analyzer = RoomAnalyzer(self.client)
            self.poi_detector = POIDetector(self.client)
    
    def _map_room_type(self, room_type: str) -> str:
        """Mappe les types Gemini vers les types du schema."""
        mapping = {
            "living_room": "living",
            "bedroom": "bedroom",
            "kitchen": "kitchen",
            "bathroom": "bathroom",
            "office": "office",
            "dining_room": "dining",
            "hallway": "hallway"
        }
        return mapping.get(room_type, "other")
    
    def _get_room_name(self, room_type: str) -> str:
        """Génère un nom lisible."""
        names = {
            "living_room": "Salon",
            "bedroom": "Chambre",
            "kitchen": "Cuisine",
            "bathroom": "Salle de bain",
            "office": "Bureau",
            "dining_room": "Salle à manger",
            "hallway": "Couloir"
        }
        return names.get(room_type, "Pièce")
    
    def _convert_pois_to_3d(self, pois: list) -> list:
        """Convertit POIs 2D en format 3D schema."""
        result = []
        for i, poi in enumerate(pois):
            pos = poi.get("position", {})
            result.append({
                "id": f"poi_{i+1:03d}",
                "type": poi.get("type", "other"),
                "position": [
                    pos.get("x_percent", 50) / 10,
                    pos.get("y_percent", 50) / 10,
                    0.5
                ]
            })
        return result
    
    def _generate_camera_path(self, dimensions: dict, frame_count: int) -> dict:
        """Génère un camera_path linéaire traversant la pièce."""
        width = dimensions.get("width", 5.0)
        length = dimensions.get("length", 6.0)
        height = 1.6
        
        return {
            "type": "linear",
            "keyframes": [
                {
                    "frame": 0,
                    "position": [0.5, 0.5, height],
                    "rotation": [90, 0, 0]
                },
                {
                    "frame": frame_count // 2,
                    "position": [width / 2, length / 2, height],
                    "rotation": [90, 0, 0]
                },
                {
                    "frame": frame_count - 1,
                    "position": [width - 0.5, length - 0.5, height],
                    "rotation": [90, 0, 0]
                }
            ]
        }
    
    def select_keyframes(self, 
                         frames_dir: Path,
                         count: int = 3) -> List[str]:
        """
        Sélectionne les keyframes pour l'analyse.
        
        Stratégie: début (0%), milieu (50%), fin (100%)
        
        Args:
            frames_dir: Dossier contenant les frames
            count: Nombre de keyframes
            
        Returns:
            Liste des chemins de keyframes
        """
        frames = sorted(frames_dir.glob("*.png"))
        
        if not frames:
            frames = sorted(frames_dir.glob("*.jpg"))
        
        if len(frames) < count:
            return [str(f) for f in frames]
        
        indices = [
            0,
            len(frames) // 2,
            len(frames) - 1
        ]
        
        if count > 3:
            step = len(frames) // count
            indices = [i * step for i in range(count)]
            indices[-1] = len(frames) - 1
        
        return [str(frames[i]) for i in indices[:count]]
    
    def run(self,
            frames_dir: Optional[str] = None,
            keyframe_count: int = 3) -> Dict[str, Any]:
        """
        Exécute le pipeline complet.
        
        Args:
            frames_dir: Dossier des frames (défaut: INPUT/project_id/frames)
            keyframe_count: Nombre de keyframes à analyser
            
        Returns:
            Dict avec masterplan complet
        """
        start_time = time.time()
        
        self._init_clients()
        
        if frames_dir is None:
            frames_dir = self.input_dir / "frames"
        else:
            frames_dir = Path(frames_dir)
        
        print("\n" + "=" * 60)
        print("FRÉGATE CORTEX - ANALYSE IA")
        print("=" * 60)
        
        print("\n📸 Stage 1: Sélection des keyframes")
        keyframes = self.select_keyframes(frames_dir, keyframe_count)
        print(f"   Keyframes sélectionnés: {len(keyframes)}")
        for kf in keyframes:
            print(f"      - {Path(kf).name}")
        
        print("\n🔍 Stage 2: Analyse des pièces")
        room_analysis = self.room_analyzer.analyze_keyframes(keyframes)
        
        print("\n🎯 Stage 3: Détection des Points d'Intérêt")
        
        central_frame = keyframes[len(keyframes) // 2]
        poi_data = self.poi_detector.detect_poi(central_frame)
        
        heatmap = self.poi_detector.generate_heatmap(poi_data)
        crop_center = self.poi_detector.get_crop_center(heatmap)
        
        print(f"   POI détectés: {len(poi_data.get('points_of_interest', []))}")
        print(f"   Centre optimal crop: ({crop_center[0]:.1f}%, {crop_center[1]:.1f}%)")
        
        print("\n📋 Stage 4: Génération du masterplan")
        
        total_time = time.time() - start_time
        
        est_dims = room_analysis.get("estimated_dimensions", {})
        dimensions = {
            "width": est_dims.get("width_meters", 5.0),
            "length": est_dims.get("length_meters", 6.0),
            "height": est_dims.get("height_meters", 2.8)
        }
        
        frame_count = len(list((frames_dir).glob("*.png"))) or len(list((frames_dir).glob("*.jpg"))) or 60
        
        masterplan = {
            "project_id": self.project_id,
            "version": "1.0",
            "source_video": f"{self.project_id}.mp4",
            
            "rooms": [{
                "id": "room_001",
                "name": self._get_room_name(room_analysis.get("room_type")),
                "type": self._map_room_type(room_analysis.get("room_type")),
                "style": room_analysis.get("style"),
                "dimensions": dimensions,
                "pois": self._convert_pois_to_3d(poi_data.get("points_of_interest", []))
            }],
            
            "camera_path": self._generate_camera_path(dimensions, frame_count),
            
            "metadata": {
                "duration_sec": total_time,
                "fps": 24,
                "resolution": [1920, 1080]
            }
        }
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        masterplan_path = self.output_dir / "masterplan.json"
        
        with open(masterplan_path, 'w') as f:
            json.dump(masterplan, f, indent=2)
        
        print(f"   ✅ Masterplan sauvegardé: {masterplan_path}")
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ FRÉGATE CORTEX")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Type de pièce: {masterplan['rooms'][0]['type']}")
        print(f"  Style: {masterplan['rooms'][0].get('style', 'N/A')}")
        print(f"  POI détectés: {len(masterplan['rooms'][0]['pois'])}")
        print(f"  Camera keyframes: {len(masterplan['camera_path']['keyframes'])}")
        print(f"  Appels API: {self.client.request_count}")
        print(f"  Temps total: {total_time:.1f}s")
        print("=" * 60)
        
        return masterplan


def run_cortex(project_id: str,
               frames_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer Cortex.
    
    Args:
        project_id: ID du projet
        frames_dir: Dossier des frames (optionnel)
        
    Returns:
        Masterplan généré
    """
    pipeline = CortexPipeline(project_id)
    return pipeline.run(frames_dir=frames_dir)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = run_cortex(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
