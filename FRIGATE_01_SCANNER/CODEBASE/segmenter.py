#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCANNER - Segmentation SAM
Génère des masques de détourage précis via Segment Anything Model.
"""

import os
import sys
import gc
from pathlib import Path
from typing import List, Dict, Any, Tuple
import torch
import numpy as np
from PIL import Image
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from CORE_CONFIG.paths import AI_MODELS_DIR
except ImportError:
    AI_MODELS_DIR = "/content/drive/MyDrive/EXODUS_SHARED_RESOURCES/AI_MODELS/"

SAM_MODEL_PATH = f"{AI_MODELS_DIR}sam/sam_vit_h_4b8939.pth"
SAM_MODEL_TYPE = "vit_h"

SAM_MODELS = {
    "vit_h": {
        "path": f"{AI_MODELS_DIR}sam/sam_vit_h_4b8939.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "vram_gb": 7.0
    },
    "vit_l": {
        "path": f"{AI_MODELS_DIR}sam/sam_vit_l_0b3195.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        "vram_gb": 5.0
    },
    "vit_b": {
        "path": f"{AI_MODELS_DIR}sam/sam_vit_b_01ec64.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        "vram_gb": 2.5
    }
}


class SAMSegmenter:
    """
    Segmenteur SAM pour masques de détourage précis.
    
    Utilise Segment Anything Model (Meta) pour générer des masques
    à partir de bounding boxes ou points.
    """
    
    def __init__(self,
                 model_path: str = None,
                 model_type: str = SAM_MODEL_TYPE,
                 device: str = 'cuda'):
        """
        Args:
            model_path: Chemin vers le checkpoint SAM
            model_type: 'vit_h', 'vit_l' ou 'vit_b'
            device: 'cuda' ou 'cpu'
        """
        self.model_type = model_type
        self.model_path = model_path or SAM_MODELS.get(model_type, {}).get("path", SAM_MODEL_PATH)
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.sam = None
        self.predictor = None
        self._current_image_path = None
        
        print("🎭 SAMSegmenter initialisé")
        print(f"   Modèle: {self.model_type}")
        print(f"   Checkpoint: {self.model_path}")
        print(f"   Device: {self.device}")
        
    def load_model(self):
        """Charge le modèle SAM."""
        try:
            from segment_anything import sam_model_registry, SamPredictor
        except ImportError:
            print("⚠️ segment-anything non installé, installation...")
            os.system('pip install -q git+https://github.com/facebookresearch/segment-anything.git')
            from segment_anything import sam_model_registry, SamPredictor
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"SAM checkpoint non trouvé: {self.model_path}\n"
                f"Télécharger depuis: https://github.com/facebookresearch/segment-anything#model-checkpoints\n"
                f"URL directe: {SAM_MODELS.get(self.model_type, {}).get('url', 'N/A')}"
            )
        
        print(f"📥 Chargement SAM: {self.model_type}...")
        
        self.sam = sam_model_registry[self.model_type](checkpoint=self.model_path)
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)
        
        print(f"✅ SAM chargé: {self.model_type}")
        
        if self.device == 'cuda':
            vram_used = torch.cuda.memory_allocated() / 1e9
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM utilisée: {vram_used:.2f} GB")
    
    def _set_image(self, image_path: str):
        """Charge et encode une image pour SAM."""
        if self._current_image_path == image_path:
            return
            
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        self.predictor.set_image(image)
        self._current_image_path = image_path
        
    def segment_from_box(self,
                         image_path: str,
                         bounding_box: Dict[str, int],
                         return_all_masks: bool = False) -> Dict[str, Any]:
        """
        Génère un masque à partir d'une bounding box.
        
        Args:
            image_path: Chemin de l'image
            bounding_box: {"x1": int, "y1": int, "x2": int, "y2": int} en pixels
            return_all_masks: Retourner tous les masques ou seulement le meilleur
            
        Returns:
            Dict avec masque et métadonnées
        """
        if self.predictor is None:
            self.load_model()
            
        self._set_image(image_path)
        
        box = np.array([
            bounding_box["x1"],
            bounding_box["y1"],
            bounding_box["x2"],
            bounding_box["y2"]
        ])
        
        masks, scores, logits = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=box[None, :],
            multimask_output=return_all_masks
        )
        
        best_idx = np.argmax(scores)
        best_mask = masks[best_idx]
        best_score = scores[best_idx]
        
        y_indices, x_indices = np.where(best_mask)
        if len(x_indices) > 0:
            tight_bbox = {
                "x1": int(x_indices.min()),
                "y1": int(y_indices.min()),
                "x2": int(x_indices.max()),
                "y2": int(y_indices.max())
            }
        else:
            tight_bbox = bounding_box
        
        return {
            "mask": best_mask,
            "score": float(best_score),
            "area_pixels": int(best_mask.sum()),
            "area_percent": round(best_mask.sum() / best_mask.size * 100, 2),
            "tight_bbox": tight_bbox,
            "all_masks": masks if return_all_masks else None,
            "all_scores": scores.tolist() if return_all_masks else None
        }
    
    def segment_from_point(self,
                           image_path: str,
                           point: Tuple[int, int],
                           point_label: int = 1) -> Dict[str, Any]:
        """
        Génère un masque à partir d'un point.
        
        Args:
            image_path: Chemin de l'image
            point: (x, y) coordonnées du point
            point_label: 1 = foreground, 0 = background
            
        Returns:
            Dict avec masque et métadonnées
        """
        if self.predictor is None:
            self.load_model()
            
        self._set_image(image_path)
        
        input_point = np.array([[point[0], point[1]]])
        input_label = np.array([point_label])
        
        masks, scores, logits = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True
        )
        
        best_idx = np.argmax(scores)
        best_mask = masks[best_idx]
        best_score = scores[best_idx]
        
        return {
            "mask": best_mask,
            "score": float(best_score),
            "area_pixels": int(best_mask.sum()),
            "area_percent": round(best_mask.sum() / best_mask.size * 100, 2)
        }
    
    def segment_from_points(self,
                            image_path: str,
                            points: List[Tuple[int, int]],
                            labels: List[int]) -> Dict[str, Any]:
        """
        Génère un masque à partir de plusieurs points.
        
        Args:
            image_path: Chemin de l'image
            points: Liste de (x, y) coordonnées
            labels: Liste de labels (1 = foreground, 0 = background)
            
        Returns:
            Dict avec masque et métadonnées
        """
        if self.predictor is None:
            self.load_model()
            
        self._set_image(image_path)
        
        input_points = np.array(points)
        input_labels = np.array(labels)
        
        masks, scores, logits = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )
        
        best_idx = np.argmax(scores)
        best_mask = masks[best_idx]
        best_score = scores[best_idx]
        
        return {
            "mask": best_mask,
            "score": float(best_score),
            "area_pixels": int(best_mask.sum()),
            "area_percent": round(best_mask.sum() / best_mask.size * 100, 2)
        }
    
    def segment_detections(self,
                           image_path: str,
                           detections: List[Dict]) -> List[Dict]:
        """
        Génère des masques pour toutes les détections YOLO.
        
        Args:
            image_path: Chemin de l'image
            detections: Liste de détections YOLO avec bounding_box_pixels
            
        Returns:
            Liste de détections enrichies avec masques
        """
        if self.predictor is None:
            self.load_model()
            
        results = []
        
        print(f"🎭 Segmentation de {len(detections)} détections...")
        
        for i, det in enumerate(detections):
            box = det.get("bounding_box_pixels")
            if not box:
                print(f"   ⚠️ Détection {i} sans bounding_box_pixels, ignorée")
                continue
            
            try:
                seg_result = self.segment_from_box(image_path, box)
                
                enriched = {
                    **det,
                    "mask": seg_result["mask"],
                    "segmentation_score": seg_result["score"],
                    "mask_area_percent": seg_result["area_percent"],
                    "tight_bbox": seg_result["tight_bbox"]
                }
                results.append(enriched)
                
            except Exception as e:
                print(f"   ❌ Erreur segmentation détection {i}: {e}")
                results.append({**det, "mask": None, "segmentation_error": str(e)})
        
        successful = sum(1 for r in results if r.get("mask") is not None)
        print(f"✅ Segmentation terminée: {successful}/{len(detections)} réussies")
        
        return results
    
    def save_mask(self, mask: np.ndarray, output_path: str, as_alpha: bool = False):
        """
        Sauvegarde un masque en PNG.
        
        Args:
            mask: Array booléen (H, W)
            output_path: Chemin de sortie
            as_alpha: Sauvegarder en RGBA avec masque comme alpha
        """
        if as_alpha:
            mask_rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
            mask_rgba[..., 3] = (mask * 255).astype(np.uint8)
            Image.fromarray(mask_rgba, mode='RGBA').save(output_path)
        else:
            mask_img = (mask * 255).astype(np.uint8)
            cv2.imwrite(str(output_path), mask_img)
    
    def save_masked_image(self,
                          image_path: str,
                          mask: np.ndarray,
                          output_path: str,
                          background: str = 'transparent'):
        """
        Sauvegarde l'image avec le masque appliqué.
        
        Args:
            image_path: Chemin de l'image source
            mask: Masque booléen
            output_path: Chemin de sortie
            background: 'transparent', 'white', 'black' ou couleur hex
        """
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        
        if background == 'transparent':
            image[..., 3] = (mask * 255).astype(np.uint8)
        else:
            if background == 'white':
                bg_color = [255, 255, 255, 255]
            elif background == 'black':
                bg_color = [0, 0, 0, 255]
            else:
                bg_color = [128, 128, 128, 255]
            
            bg = np.full(image.shape, bg_color, dtype=np.uint8)
            mask_3d = np.stack([mask] * 4, axis=-1)
            image = np.where(mask_3d, image, bg)
        
        Image.fromarray(image, mode='RGBA').save(output_path)
    
    def cleanup(self):
        """Libère la VRAM."""
        if self.sam is not None:
            del self.sam
            self.sam = None
        if self.predictor is not None:
            del self.predictor
            self.predictor = None
        self._current_image_path = None
        torch.cuda.empty_cache()
        gc.collect()
        print("🧹 SAM - VRAM libérée")


def segment_from_detection(image_path: str,
                           bounding_box: Dict[str, int],
                           model_type: str = "vit_h") -> Dict[str, Any]:
    """
    Fonction utilitaire pour segmentation rapide.
    
    Args:
        image_path: Chemin vers l'image
        bounding_box: {"x1", "y1", "x2", "y2"} en pixels
        model_type: Type de modèle SAM
        
    Returns:
        Dict avec masque et métadonnées
    """
    segmenter = SAMSegmenter(model_type=model_type)
    try:
        return segmenter.segment_from_box(image_path, bounding_box)
    finally:
        segmenter.cleanup()


if __name__ == "__main__":
    print("SAMSegmenter - Test basique")
    print(f"Modèles disponibles: {list(SAM_MODELS.keys())}")
    print(f"Chemin par défaut: {SAM_MODEL_PATH}")
