#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCANNER - Estimateur de Profondeur
F01-004 à F01-009

Génère des depth maps via Depth Anything V2.
"""

import os
import sys
import time
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

import torch
import numpy as np
from PIL import Image
import cv2

try:
    from config.paths import AI_MODELS_DIR, DEPTH_MODEL_PATH, DEPTH_MODEL_BASE_PATH
except ImportError:
    AI_MODELS_DIR = "/content/drive/MyDrive/EXODUS_SHARED_RESOURCES/AI_MODELS/"
    DEPTH_MODEL_PATH = AI_MODELS_DIR + "depth_anything_v2/depth_anything_v2_vitl.pth"
    DEPTH_MODEL_BASE_PATH = AI_MODELS_DIR + "depth_anything_v2/depth_anything_v2_vitb.pth"


class DepthEstimator:
    """
    Estimateur de profondeur utilisant Depth Anything V2.
    
    Optimisé pour Google Colab T4 (16GB VRAM).
    """
    
    MODEL_PATHS = {
        'vit-large': DEPTH_MODEL_PATH,
        'vit-base': DEPTH_MODEL_BASE_PATH,
    }
    
    MODEL_CONFIG = {
        'vit-large': {'max_batch': 1, 'vram_gb': 4.5},
        'vit-base': {'max_batch': 2, 'vram_gb': 2.0},
    }
    
    def __init__(self, 
                 model_type: str = 'vit-large',
                 device: str = 'cuda',
                 output_dir: str = './depth_maps'):
        """
        Args:
            model_type: 'vit-large' ou 'vit-base'
            device: 'cuda' ou 'cpu'
            output_dir: Dossier pour les depth maps
        """
        self.model_type = model_type
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.transform = None
        
        print(f"🧠 DepthEstimator initialisé")
        print(f"   Modèle: {model_type}")
        print(f"   Device: {self.device}")
        if self.device == 'cuda':
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    def load_model(self, model_path: Optional[str] = None):
        """Charge le modèle Depth Anything V2."""
        
        if model_path is None:
            model_path = self.MODEL_PATHS.get(self.model_type)
            
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modèle non trouvé: {model_path}\n"
                f"Téléchargez depuis: https://huggingface.co/depth-anything/Depth-Anything-V2-Large"
            )
        
        print(f"📥 Chargement modèle: {model_path}")
        start = time.time()
        
        try:
            from depth_anything_v2.dpt import DepthAnythingV2
        except ImportError:
            print("⚠️ depth_anything_v2 non installé, installation...")
            os.system('pip install -q git+https://github.com/DepthAnything/Depth-Anything-V2.git')
            from depth_anything_v2.dpt import DepthAnythingV2
        
        if 'large' in self.model_type or 'vitl' in model_path.lower():
            encoder = 'vitl'
            features = 256
            out_channels = [256, 512, 1024, 1024]
        else:
            encoder = 'vitb'
            features = 128
            out_channels = [96, 192, 384, 768]
        
        self.model = DepthAnythingV2(
            encoder=encoder,
            features=features,
            out_channels=out_channels
        )
        
        state_dict = torch.load(model_path, map_location='cpu')
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        elapsed = time.time() - start
        print(f"✅ Modèle chargé en {elapsed:.1f}s")
        
        if self.device == 'cuda':
            vram_used = torch.cuda.memory_allocated() / 1e9
            print(f"   VRAM utilisée: {vram_used:.2f} GB")
    
    def estimate_depth(self, image_path: str) -> np.ndarray:
        """
        Estime la profondeur d'une seule image.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            numpy array (H, W) avec valeurs de profondeur normalisées [0, 1]
        """
        if self.model is None:
            self.load_model()
        
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Impossible de charger: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        with torch.no_grad():
            depth = self.model.infer_image(image)
        
        depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)
        
        return depth
    
    def save_depth_map(self, depth: np.ndarray, output_path: str, bit_depth: int = 16):
        """
        Sauvegarde une depth map en PNG 16-bit.
        
        Args:
            depth: Array normalisé [0, 1]
            output_path: Chemin de sortie
            bit_depth: 8 ou 16 bits
        """
        if bit_depth == 16:
            depth_16bit = (depth * 65535).astype(np.uint16)
            cv2.imwrite(str(output_path), depth_16bit)
        else:
            depth_8bit = (depth * 255).astype(np.uint8)
            cv2.imwrite(str(output_path), depth_8bit)
    
    def process_batch(self, 
                      frame_paths: List[str],
                      batch_size: int = 1,
                      save_16bit: bool = True) -> Dict[str, Any]:
        """
        Traite un batch de frames.
        
        Args:
            frame_paths: Liste des chemins d'images
            batch_size: Taille du batch (1 recommandé pour VRAM)
            save_16bit: Sauvegarder en 16-bit
            
        Returns:
            Dict avec statistiques et chemins des depth maps
        """
        if self.model is None:
            self.load_model()
        
        depth_dir = self.output_dir / 'depth_maps'
        depth_dir.mkdir(exist_ok=True)
        
        print(f"🔍 Traitement de {len(frame_paths)} frames...")
        
        results = []
        total_time = 0
        
        for i, frame_path in enumerate(frame_paths):
            frame_name = Path(frame_path).stem
            depth_path = depth_dir / f"depth_{frame_name.replace('frame_', '')}.png"
            
            start = time.time()
            
            try:
                depth = self.estimate_depth(frame_path)
                
                self.save_depth_map(depth, str(depth_path), 
                                    bit_depth=16 if save_16bit else 8)
                
                elapsed = time.time() - start
                total_time += elapsed
                
                results.append({
                    'frame': frame_path,
                    'depth_map': str(depth_path),
                    'time': elapsed,
                    'status': 'success'
                })
                
                if (i + 1) % 10 == 0 or i == len(frame_paths) - 1:
                    avg_time = total_time / (i + 1)
                    eta = avg_time * (len(frame_paths) - i - 1)
                    print(f"   [{i+1}/{len(frame_paths)}] {elapsed:.2f}s/frame | ETA: {eta:.0f}s")
                
            except Exception as e:
                results.append({
                    'frame': frame_path,
                    'error': str(e),
                    'status': 'failed'
                })
                print(f"   ❌ Erreur frame {i}: {e}")
            
            if (i + 1) % 50 == 0:
                torch.cuda.empty_cache()
                gc.collect()
        
        successful = sum(1 for r in results if r['status'] == 'success')
        avg_time = total_time / successful if successful else 0
        
        print(f"✅ Depth estimation terminée")
        print(f"   Réussies: {successful}/{len(frame_paths)}")
        print(f"   Temps moyen: {avg_time:.2f}s/frame")
        print(f"   Temps total: {total_time:.1f}s")
        
        return {
            'output_dir': str(depth_dir),
            'total_frames': len(frame_paths),
            'successful': successful,
            'failed': len(frame_paths) - successful,
            'avg_time_per_frame': avg_time,
            'total_time': total_time,
            'results': results
        }
    
    def cleanup(self):
        """Libère la VRAM."""
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
        gc.collect()
        print("🧹 VRAM libérée")


def estimate_depth_for_frames(frame_paths: List[str],
                               output_dir: str,
                               model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour estimation rapide.
    
    Args:
        frame_paths: Liste des chemins d'images
        output_dir: Dossier de sortie
        model_path: Chemin optionnel du modèle
        
    Returns:
        Résultats du traitement
    """
    estimator = DepthEstimator(output_dir=output_dir)
    if model_path:
        estimator.load_model(model_path)
    
    try:
        result = estimator.process_batch(frame_paths)
    finally:
        estimator.cleanup()
    
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        frames_dir = Path(sys.argv[1])
        frames = sorted(frames_dir.glob('*.png'))[:5]
        
        result = estimate_depth_for_frames(
            [str(f) for f in frames],
            "./test_depth"
        )
        print(json.dumps({k: v for k, v in result.items() if k != 'results'}, indent=2))
