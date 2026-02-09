"""
EXODUS-SPECULUM - Mock Generators
Générateurs de données mock pour tests sans ML.

Ces générateurs produisent des données synthétiques qui respectent
les contrats de sortie sans nécessiter de modèles ML ou Blender.
"""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import random
import string


def generate_mock_depth(
    width: int = 960,
    height: int = 540,
    near: float = 10000,
    far: float = 60000,
    noise_std: float = 500
) -> np.ndarray:
    """
    Génère une depth map factice mais réaliste.
    
    Simule une pièce avec:
    - Gradient de profondeur (proche en bas, loin en haut)
    - Bruit gaussien pour réalisme
    - Valeurs dans la plage uint16
    
    Args:
        width: Largeur en pixels
        height: Hauteur en pixels
        near: Valeur depth proche
        far: Valeur depth lointaine
        noise_std: Écart-type du bruit
        
    Returns:
        np.ndarray de shape (height, width) dtype uint16
    """
    y = np.linspace(0, 1, height)[:, np.newaxis]
    x = np.linspace(0, 1, width)[np.newaxis, :]
    
    base_depth = (1 - y * 0.7) * (far - near) + near
    x_variation = x * 2000 - 1000
    noise = np.random.normal(0, noise_std, (height, width))
    depth = base_depth + x_variation + noise
    
    return np.clip(depth, 0, 65535).astype(np.uint16)


def generate_mock_frame(
    width: int = 960,
    height: int = 540,
    room_color: Tuple[int, int, int] = (120, 140, 160)
) -> np.ndarray:
    """
    Génère une frame RGB factice simulant un intérieur.
    
    Args:
        width: Largeur en pixels
        height: Hauteur en pixels
        room_color: Couleur de base (R, G, B)
        
    Returns:
        np.ndarray de shape (height, width, 3) dtype uint8
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    r, g, b = room_color
    x_grad = np.linspace(-30, 30, width)[np.newaxis, :]
    y_grad = np.linspace(-20, 40, height)[:, np.newaxis]
    
    frame[:, :, 0] = np.clip(r + x_grad, 0, 255)
    frame[:, :, 1] = np.clip(g + y_grad, 0, 255)
    frame[:, :, 2] = b
    
    return frame


def generate_mock_masterplan(
    project_id: Optional[str] = None,
    num_rooms: int = 1,
    num_pois: int = 3
) -> Dict[str, Any]:
    """
    Génère un masterplan factice mais valide selon le schema.
    
    Args:
        project_id: ID du projet (généré si None)
        num_rooms: Nombre de pièces
        num_pois: Nombre de POIs par pièce
        
    Returns:
        Dict conforme au masterplan_schema.json
    """
    if project_id is None:
        project_id = "mock_" + "".join(random.choices(string.ascii_lowercase, k=6))
    
    room_types = ["living", "bedroom", "kitchen", "bathroom", "office"]
    poi_types = ["sofa", "table", "chair", "bed", "lamp", "plant", "shelf"]
    
    rooms = []
    for i in range(num_rooms):
        pois = []
        for j in range(num_pois):
            pois.append({
                "id": f"poi_{i}_{j}",
                "type": random.choice(poi_types),
                "position": [
                    round(random.uniform(0.5, 4.5), 2),
                    round(random.uniform(0.5, 5.5), 2),
                    round(random.uniform(0.3, 1.2), 2)
                ]
            })
        
        rooms.append({
            "id": f"room_{i:03d}",
            "name": f"Room {i + 1}",
            "type": room_types[i % len(room_types)],
            "dimensions": {
                "width": round(random.uniform(3.0, 6.0), 1),
                "length": round(random.uniform(4.0, 8.0), 1),
                "height": round(random.uniform(2.4, 3.2), 1)
            },
            "pois": pois
        })
    
    keyframes = [
        {"frame": 0, "position": [0, 0, 1.6], "rotation": [90, 0, 0]},
        {"frame": 30, "position": [2.5, 0, 1.6], "rotation": [90, 15, 0]},
        {"frame": 60, "position": [5, 0, 1.6], "rotation": [90, 0, 0]},
    ]
    
    return {
        "project_id": project_id,
        "version": "1.0",
        "rooms": rooms,
        "camera_path": {
            "type": "linear",
            "keyframes": keyframes
        },
        "metadata": {
            "duration_sec": 60,
            "fps": 24,
            "resolution": [1920, 1080]
        }
    }


def generate_mock_spatial_data(
    frame_count: int = 10,
    detections_per_frame: int = 5
) -> Dict[str, Any]:
    """
    Génère des données spatiales factices (F01 SCANNER output).
    
    Args:
        frame_count: Nombre de frames
        detections_per_frame: Nombre de détections par frame
        
    Returns:
        Dict conforme au format spatial_data.json
    """
    object_classes = ["sofa", "chair", "table", "lamp", "plant", "bed", "shelf"]
    
    frames = []
    for i in range(frame_count):
        detections = []
        for j in range(detections_per_frame):
            x = random.randint(100, 800)
            y = random.randint(100, 400)
            w = random.randint(50, 200)
            h = random.randint(50, 200)
            
            detections.append({
                "id": f"det_{i}_{j}",
                "class": random.choice(object_classes),
                "confidence": round(random.uniform(0.7, 0.99), 3),
                "bbox": [x, y, x + w, y + h],
                "center": [x + w // 2, y + h // 2]
            })
        
        frames.append({
            "frame_index": i,
            "timestamp_ms": i * 100,
            "detections": detections,
            "depth_stats": {
                "min": random.randint(5000, 10000),
                "max": random.randint(50000, 60000),
                "mean": random.randint(25000, 35000)
            }
        })
    
    return {
        "project_id": "mock_spatial",
        "frame_count": frame_count,
        "frames": frames,
        "detections": {
            "total": frame_count * detections_per_frame,
            "classes": list(set(object_classes))
        }
    }


def generate_mock_depth_batch(
    output_dir: str,
    count: int = 10,
    width: int = 960,
    height: int = 540
) -> List[str]:
    """
    Génère un batch de depth maps et les sauvegarde.
    
    Args:
        output_dir: Répertoire de sortie
        count: Nombre de depth maps
        width: Largeur
        height: Hauteur
        
    Returns:
        Liste des chemins créés
    """
    from pathlib import Path
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    paths = []
    for i in range(count):
        depth = generate_mock_depth(width, height)
        file_path = out_path / f"depth_{i:06d}.npz"
        np.savez_compressed(file_path, depth=depth)
        paths.append(str(file_path))
    
    return paths
