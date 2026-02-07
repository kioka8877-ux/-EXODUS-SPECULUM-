#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate CORTEX - Pipeline Complet
Orchestre l'analyse IA et génère le masterplan.json.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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
        
        print(f"🧠 Cortex Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Input: {self.input_dir}")
        print(f"   Output: {self.output_dir}")
    
    def _init_clients(self):
        """Initialise les clients Gemini (lazy loading)."""
        if self.client is None:
            self.client = GeminiClient()
            self.room_analyzer = RoomAnalyzer(self.client)
            self.poi_detector = POIDetector(self.client)
    
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
        
        masterplan = {
            "project_id": self.project_id,
            "generated_at": datetime.now().isoformat(),
            "gemini_model": GeminiClient.MODEL_NAME,
            "keyframes_analyzed": len(keyframes),
            
            "room": {
                "type": room_analysis.get("room_type"),
                "style": room_analysis.get("style"),
                "dimensions": room_analysis.get("estimated_dimensions"),
            },
            
            "materials": room_analysis.get("materials", []),
            
            "furniture": room_analysis.get("furniture", []),
            
            "lighting": room_analysis.get("lighting"),
            
            "poi": {
                "points": poi_data.get("points_of_interest", []),
                "primary_focal_point": poi_data.get("primary_focal_point"),
                "heatmap_32x32": heatmap.tolist(),
                "optimal_crop_center": {
                    "x_percent": crop_center[0],
                    "y_percent": crop_center[1]
                }
            },
            
            "processing": {
                "time_seconds": total_time,
                "api_calls": self.client.request_count
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
        print(f"  Type de pièce: {masterplan['room']['type']}")
        print(f"  Style: {masterplan['room']['style']}")
        print(f"  Meubles détectés: {len(masterplan['furniture'])}")
        print(f"  POI détectés: {len(masterplan['poi']['points'])}")
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
