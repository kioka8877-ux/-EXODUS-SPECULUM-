#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCANNER - Détecteur d'Objets YOLOv8
Classes COCO80 pertinentes pour l'immobilier.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import torch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from CORE_CONFIG.paths import SHARED_RESOURCES, AI_MODELS_DIR
except ImportError:
    SHARED_RESOURCES = "/content/drive/MyDrive/EXODUS_SHARED_RESOURCES/"
    AI_MODELS_DIR = f"{SHARED_RESOURCES}AI_MODELS/"

REAL_ESTATE_CLASSES = {
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    68: "microwave",
    69: "oven",
    70: "toaster",
    71: "sink",
    72: "refrigerator",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
    77: "teddy bear",
    78: "hair drier",
    79: "toothbrush",
}

YOLO_MODEL_PATH = f"{AI_MODELS_DIR}yolov8/yolov8x.pt"


class ObjectDetector:
    """
    Détecteur d'objets YOLOv8 pour l'immobilier.
    
    Utilise YOLOv8x pour une détection haute précision des objets
    pertinents dans les scènes immobilières.
    """
    
    def __init__(self,
                 model_path: str = None,
                 confidence_threshold: float = 0.5,
                 device: str = 'cuda'):
        """
        Args:
            model_path: Chemin vers le modèle YOLOv8 (.pt)
            confidence_threshold: Seuil de confiance [0, 1]
            device: 'cuda' ou 'cpu'
        """
        self.model_path = model_path or YOLO_MODEL_PATH
        self.confidence = confidence_threshold
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model = None
        
        print("🎯 ObjectDetector initialisé")
        print(f"   Modèle: {self.model_path}")
        print(f"   Device: {self.device}")
        print(f"   Confidence: {self.confidence}")
        
    def load_model(self):
        """Charge le modèle YOLOv8."""
        try:
            from ultralytics import YOLO
        except ImportError:
            print("⚠️ ultralytics non installé, installation...")
            os.system('pip install -q ultralytics>=8.0.0')
            from ultralytics import YOLO
        
        if not os.path.exists(self.model_path):
            print(f"⚠️ Modèle non trouvé: {self.model_path}")
            print("   Téléchargement du modèle par défaut...")
            self.model = YOLO('yolov8x.pt')
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        else:
            self.model = YOLO(self.model_path)
        
        print(f"✅ YOLOv8 chargé: {self.model_path}")
        
        if self.device == 'cuda':
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Détecte les objets dans une image.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Liste de détections avec bounding boxes et métadonnées
        """
        if self.model is None:
            self.load_model()
            
        results = self.model(image_path, conf=self.confidence, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            img_h, img_w = result.orig_shape
            
            for i, box in enumerate(boxes):
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                conf = float(box.conf[0])
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detection = {
                    "id": f"det_{i:03d}",
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(conf, 3),
                    "bounding_box": {
                        "x_min_percent": round(x1 / img_w * 100, 2),
                        "y_min_percent": round(y1 / img_h * 100, 2),
                        "x_max_percent": round(x2 / img_w * 100, 2),
                        "y_max_percent": round(y2 / img_h * 100, 2)
                    },
                    "bounding_box_pixels": {
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2)
                    },
                    "image_size": {
                        "width": img_w,
                        "height": img_h
                    },
                    "is_real_estate_relevant": class_id in REAL_ESTATE_CLASSES
                }
                detections.append(detection)
        
        relevant = [d for d in detections if d["is_real_estate_relevant"]]
        
        print(f"🎯 Détections: {len(relevant)} objets pertinents / {len(detections)} total")
        return relevant
    
    def detect_all(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Détecte TOUS les objets (pas de filtre immobilier).
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Liste complète des détections
        """
        if self.model is None:
            self.load_model()
            
        results = self.model(image_path, conf=self.confidence, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            img_h, img_w = result.orig_shape
            
            for i, box in enumerate(boxes):
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                conf = float(box.conf[0])
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detection = {
                    "id": f"det_{i:03d}",
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(conf, 3),
                    "bounding_box": {
                        "x_min_percent": round(x1 / img_w * 100, 2),
                        "y_min_percent": round(y1 / img_h * 100, 2),
                        "x_max_percent": round(x2 / img_w * 100, 2),
                        "y_max_percent": round(y2 / img_h * 100, 2)
                    },
                    "bounding_box_pixels": {
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2)
                    },
                    "image_size": {
                        "width": img_w,
                        "height": img_h
                    },
                    "is_real_estate_relevant": class_id in REAL_ESTATE_CLASSES
                }
                detections.append(detection)
        
        print(f"🎯 Détections totales: {len(detections)} objets")
        return detections
    
    def detect_batch(self, image_paths: List[str]) -> Dict[str, List]:
        """
        Détecte dans plusieurs images.
        
        Args:
            image_paths: Liste des chemins d'images
            
        Returns:
            Dict {image_path: [detections]}
        """
        results = {}
        total_detections = 0
        
        print(f"🔍 Détection batch: {len(image_paths)} images...")
        
        for i, path in enumerate(image_paths):
            try:
                detections = self.detect(path)
                results[path] = detections
                total_detections += len(detections)
                
                if (i + 1) % 10 == 0 or i == len(image_paths) - 1:
                    print(f"   [{i+1}/{len(image_paths)}] {len(detections)} détections")
                    
            except Exception as e:
                print(f"   ❌ Erreur {path}: {e}")
                results[path] = []
        
        print(f"✅ Batch terminé: {total_detections} détections totales")
        return results
    
    def get_class_counts(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Compte les occurrences par classe.
        
        Args:
            detections: Liste de détections
            
        Returns:
            Dict {class_name: count}
        """
        counts = {}
        for det in detections:
            name = det["class_name"]
            counts[name] = counts.get(name, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))


def detect_objects_in_image(image_path: str,
                            confidence: float = 0.5,
                            model_path: Optional[str] = None) -> List[Dict]:
    """
    Fonction utilitaire pour détection rapide.
    
    Args:
        image_path: Chemin vers l'image
        confidence: Seuil de confiance
        model_path: Chemin optionnel du modèle
        
    Returns:
        Liste des détections
    """
    detector = ObjectDetector(
        model_path=model_path,
        confidence_threshold=confidence
    )
    return detector.detect(image_path)


if __name__ == "__main__":
    import json
    if len(sys.argv) > 1:
        detections = detect_objects_in_image(sys.argv[1])
        print(json.dumps(detections, indent=2))
