#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCANNER - Pipeline Complet
Orchestre l'extraction et l'estimation de profondeur.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from config.paths import F01_INPUT, F01_OUTPUT
except ImportError:
    F01_INPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_01_SCANNER/INPUT/"
    F01_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_01_SCANNER/OUTPUT/"

from .frame_extractor import FrameExtractor
from .depth_estimator import DepthEstimator


class ScannerPipeline:
    """
    Pipeline complet de la Frégate SCANNER.
    
    Workflow:
    1. Extraction frames (FFmpeg)
    2. Estimation profondeur (Depth Anything V2)
    3. Export spatial_data.json
    """
    
    def __init__(self, 
                 project_id: str,
                 output_base: str = None):
        """
        Args:
            project_id: Identifiant unique du projet
            output_base: Dossier racine de sortie (défaut: F01_OUTPUT)
        """
        if output_base is None:
            output_base = F01_OUTPUT
        
        self.project_id = project_id
        self.output_dir = Path(output_base) / project_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.frame_extractor = None
        self.depth_estimator = None
        
        print(f"🔍 Scanner Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Output: {self.output_dir}")
    
    def run(self, 
            video_path: str,
            fps: float = 2.0,
            depth_model: str = 'vit-large',
            skip_depth: bool = False) -> Dict[str, Any]:
        """
        Exécute le pipeline complet.
        
        Args:
            video_path: Chemin de la vidéo source
            fps: Frames par seconde à extraire
            depth_model: Modèle de profondeur
            skip_depth: Sauter l'estimation de profondeur
            
        Returns:
            Dict avec tous les résultats
        """
        start_time = time.time()
        results = {
            'project_id': self.project_id,
            'video_source': video_path,
            'timestamp': datetime.now().isoformat(),
            'stages': {}
        }
        
        print("\n" + "=" * 60)
        print("STAGE 1: Extraction des frames")
        print("=" * 60)
        
        self.frame_extractor = FrameExtractor(
            output_dir=str(self.output_dir),
            fps=fps
        )
        
        extraction_result = self.frame_extractor.extract_frames(video_path)
        results['stages']['extraction'] = extraction_result
        
        if not skip_depth and extraction_result['frame_count'] > 0:
            print("\n" + "=" * 60)
            print("STAGE 2: Estimation de profondeur")
            print("=" * 60)
            
            self.depth_estimator = DepthEstimator(
                model_type=depth_model,
                output_dir=str(self.output_dir)
            )
            
            depth_result = self.depth_estimator.process_batch(
                extraction_result['frames']
            )
            results['stages']['depth'] = depth_result
            
            self.depth_estimator.cleanup()
        else:
            results['stages']['depth'] = {'skipped': True}
        
        print("\n" + "=" * 60)
        print("STAGE 3: Export données spatiales")
        print("=" * 60)
        
        total_time = time.time() - start_time
        
        spatial_data = {
            'project_id': self.project_id,
            'generated_at': datetime.now().isoformat(),
            'video': extraction_result.get('video_info', {}),
            'frames': {
                'count': extraction_result['frame_count'],
                'fps': fps,
                'directory': extraction_result['output_dir']
            },
            'depth_maps': {
                'available': not skip_depth,
                'model': depth_model if not skip_depth else None,
                'directory': str(self.output_dir / 'depth_maps') if not skip_depth else None
            },
            'processing_time_seconds': total_time
        }
        
        spatial_path = self.output_dir / 'spatial_data.json'
        with open(spatial_path, 'w') as f:
            json.dump(spatial_data, f, indent=2)
        
        print(f"✅ spatial_data.json exporté: {spatial_path}")
        
        results['spatial_data'] = spatial_data
        results['total_time'] = total_time
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ FRÉGATE SCANNER")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Frames extraites: {extraction_result['frame_count']}")
        if not skip_depth:
            print(f"  Depth maps: {results['stages']['depth'].get('successful', 0)}")
        print(f"  Temps total: {total_time:.1f}s")
        print(f"  Output: {self.output_dir}")
        print("=" * 60)
        
        return results


def run_scanner(video_path: str,
                project_id: str,
                fps: float = 2.0,
                output_base: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer le scanner.
    
    Args:
        video_path: Chemin vidéo
        project_id: ID du projet
        fps: FPS d'extraction
        output_base: Dossier de sortie (optionnel)
        
    Returns:
        Résultats du pipeline
    """
    if output_base is None:
        output_base = F01_OUTPUT
    
    pipeline = ScannerPipeline(project_id, output_base)
    return pipeline.run(video_path, fps=fps)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        result = run_scanner(sys.argv[1], sys.argv[2])
        print(json.dumps(result, indent=2, default=str))
