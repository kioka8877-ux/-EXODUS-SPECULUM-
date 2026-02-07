#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO - Pipeline Orchestrateur
Anime la caméra pour simuler un tournage iPhone tenu à la main.

Input: scene_furnished.blend (depuis F05) + masterplan.json (POI heatmap)
Output: scene_animated.blend avec caméra animée style "visite iPhone"

Philosophie: L'Œil de l'Envie
Recréer le style "Femme qui filme avec son iPhone" pour maximiser
l'authenticité et la viralité sur TikTok/Reels.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from CORE_CONFIG.paths import (
        F04_OUTPUT, F05_OUTPUT, F00_OUTPUT,
        F05_CODEBASE, F05_INPUT,
        PathConfig
    )
except ImportError:
    F04_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_04_LOGISTIQUE/OUTPUT/"
    F05_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_05_DIRECTEUR_PHOTO/OUTPUT/"
    F05_INPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_05_DIRECTEUR_PHOTO/INPUT/"
    F05_CODEBASE = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_05_DIRECTEUR_PHOTO/"
    F00_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_00_CORTEX/OUTPUT/"
    PathConfig = None

from .camera_humanizer import CameraHumanizer
from .shakify import Shakify
from .smart_crop import SmartCrop
from .format_adapter import FormatAdapter


class DirecteurPipeline:
    """
    Pipeline complet de la Frégate DIRECTEUR PHOTO.
    
    Workflow:
    1. Charger scene_furnished.blend (depuis F05-LOGISTIQUE)
    2. Trouver/créer la caméra principale
    3. Setup iPhone (focale 26mm)
    4. Charger POI heatmap depuis masterplan
    5. Appliquer walking bounce (oscillation Z)
    6. Appliquer shakify (bruit de Perlin rotation)
    7. Appliquer smart crop (sensor shift vers POI)
    8. Configurer format de sortie (VERTICAL pour TikTok)
    9. Compenser FOV si nécessaire
    10. Sauvegarder scene_animated.blend
    """
    
    EXODUS_VERSION = "0.6.0"
    DEFAULT_FPS = 24
    DEFAULT_DURATION_SECONDS = 30.0
    
    def __init__(self, project_id: str, output_base: Optional[str] = None):
        """
        Args:
            project_id: Identifiant unique du projet
            output_base: Dossier racine de sortie (défaut: F06_OUTPUT)
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("🚫 Blender Python (bpy) not available. Run in Blender environment.")
        
        if output_base is None:
            output_base = F06_OUTPUT
        
        self.project_id = project_id
        self.output_dir = Path(output_base) / project_id
        
        self.humanizer = CameraHumanizer(verbose=True)
        self.shakify = Shakify(seed=42, verbose=True)
        self.smart_crop = SmartCrop(verbose=True)
        self.format_adapter = FormatAdapter(verbose=True)
        
        self.camera = None
        self.poi_heatmap: Dict = {}
        self.poi_center: tuple = (0.5, 0.5)
        
        print(f"🎬 Directeur Photo Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Output: {self.output_dir}")
    
    def _find_scene_furnished(self, scene_furnished_path: Optional[str] = None) -> str:
        """Trouve le fichier scene_furnished.blend."""
        if scene_furnished_path and os.path.exists(scene_furnished_path):
            return scene_furnished_path
        
        search_paths = [
            Path(F05_OUTPUT) / self.project_id / "scene_furnished.blend",
            Path(F06_INPUT) / self.project_id / "scene_furnished.blend",
            Path(F06_INPUT) / "scene_furnished.blend",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"🚫 scene_furnished.blend non trouvé. Cherché dans: {[str(p) for p in search_paths]}"
        )
    
    def _find_masterplan(self, masterplan_path: Optional[str] = None) -> str:
        """Trouve le fichier masterplan.json."""
        if masterplan_path and os.path.exists(masterplan_path):
            return masterplan_path
        
        search_paths = [
            Path(F00_OUTPUT) / self.project_id / "masterplan.json",
            Path(F06_INPUT) / self.project_id / "masterplan.json",
            Path(F06_INPUT) / "masterplan.json",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        print(f"⚠️ masterplan.json non trouvé - POI désactivé")
        return ""
    
    def _find_or_create_camera(self) -> Any:
        """
        Trouve la caméra principale ou en crée une.
        
        Ordre de recherche:
        1. Caméra active de la scène
        2. Caméra nommée "Camera_Main" ou "ProjectionCamera"
        3. Première caméra trouvée
        4. Création d'une nouvelle caméra
        """
        if bpy.context.scene.camera:
            return bpy.context.scene.camera
        
        cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        
        priority_names = ["Camera_Main", "ProjectionCamera", "Camera", "Main_Camera"]
        for name in priority_names:
            for cam in cameras:
                if name.lower() in cam.name.lower():
                    bpy.context.scene.camera = cam
                    return cam
        
        if cameras:
            bpy.context.scene.camera = cameras[0]
            return cameras[0]
        
        print("📷 Création d'une nouvelle caméra principale")
        cam_data = bpy.data.cameras.new(name="Camera_iPhone")
        cam_obj = bpy.data.objects.new(name="Camera_iPhone", object_data=cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (0, -5, 1.6)
        cam_obj.rotation_euler = (1.5708, 0, 0)
        bpy.context.scene.camera = cam_obj
        
        return cam_obj
    
    def _load_poi_data(self, masterplan_path: str) -> Dict:
        """Charge les données POI depuis le masterplan."""
        if not masterplan_path:
            return {}
        
        return self.smart_crop.load_poi_heatmap(masterplan_path)
    
    def _embed_metadata(
        self,
        scene_furnished_path: str,
        masterplan_path: str,
        output_format: str,
        duration_seconds: float,
        fps: int
    ) -> None:
        """Intègre les métadonnées dans la scène."""
        scene = bpy.context.scene
        
        scene["exodus_version"] = self.EXODUS_VERSION
        scene["project_id"] = self.project_id
        scene["scene_furnished_source"] = scene_furnished_path
        scene["masterplan_source"] = masterplan_path
        scene["output_format"] = output_format
        scene["duration_seconds"] = duration_seconds
        scene["fps"] = fps
        scene["poi_center"] = json.dumps(self.poi_center)
        scene["generated_at"] = datetime.now().isoformat()
        scene["frigate"] = "F06_DIRECTEUR_PHOTO"
        scene["camera_name"] = self.camera.name if self.camera else "None"
        
        print("📋 Métadonnées intégrées")
    
    def run(
        self,
        scene_furnished_path: Optional[str] = None,
        masterplan_path: Optional[str] = None,
        output_format: str = "VERTICAL",
        duration_seconds: float = DEFAULT_DURATION_SECONDS,
        fps: int = DEFAULT_FPS,
        output_path: Optional[str] = None,
        apply_walking_bounce: bool = True,
        apply_shake: bool = True,
        apply_smart_crop: bool = True,
        apply_breathing: bool = True,
        shake_intensity: Optional[float] = None,
        bounce_amplitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Exécute le pipeline complet F06-DIRECTEUR PHOTO.
        
        Args:
            scene_furnished_path: Chemin vers scene_furnished.blend (F05)
            masterplan_path: Chemin vers masterplan.json (POI heatmap)
            output_format: Format de sortie (VERTICAL, HORIZONTAL, SQUARE)
            duration_seconds: Durée de l'animation en secondes
            fps: Frames par seconde
            output_path: Chemin de sortie scene_animated.blend
            apply_walking_bounce: Active l'oscillation Z de marche
            apply_shake: Active le bruit de Perlin sur rotation
            apply_smart_crop: Active le sensor shift vers POI
            apply_breathing: Active le zoom de respiration
            shake_intensity: Override intensité du shake
            bounce_amplitude: Override amplitude du bounce
            
        Returns:
            Dict avec status et métadonnées
        """
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("🎬 FRÉGATE DIRECTEUR PHOTO - IPHONE POV HUMANIZER")
        print("=" * 60)
        
        scene_furnished_path = self._find_scene_furnished(scene_furnished_path)
        masterplan_path = self._find_masterplan(masterplan_path)
        
        if output_path is None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(self.output_dir / "scene_animated.blend")
        
        duration_frames = int(duration_seconds * fps)
        
        print(f"\n📂 Stage 1: Chargement scene_furnished.blend")
        print(f"   Source: {scene_furnished_path}")
        bpy.ops.wm.open_mainfile(filepath=scene_furnished_path)
        
        scene = bpy.context.scene
        scene.render.fps = fps
        scene.frame_start = 1
        scene.frame_end = duration_frames
        
        print(f"\n📷 Stage 2: Identification caméra principale")
        self.camera = self._find_or_create_camera()
        print(f"   Caméra: {self.camera.name}")
        
        print(f"\n📱 Stage 3: Setup caméra iPhone")
        self.humanizer.setup_iphone_camera(self.camera)
        
        if masterplan_path:
            print(f"\n👁️ Stage 4: Chargement POI heatmap")
            print(f"   Source: {masterplan_path}")
            self.poi_heatmap = self._load_poi_data(masterplan_path)
            self.poi_center = self.smart_crop.calculate_poi_center(self.poi_heatmap)
            print(f"   POI center: ({self.poi_center[0]:.3f}, {self.poi_center[1]:.3f})")
        else:
            print(f"\n👁️ Stage 4: POI désactivé (pas de masterplan)")
            self.poi_center = (0.5, 0.5)
        
        if apply_walking_bounce:
            print(f"\n🚶 Stage 5: Application walking bounce")
            self.humanizer.add_walking_bounce(
                self.camera, 
                duration_frames, 
                fps=fps,
                amplitude=bounce_amplitude
            )
        else:
            print(f"\n🚶 Stage 5: Walking bounce désactivé")
        
        if apply_shake:
            print(f"\n🎲 Stage 6: Application rotation shake (Perlin)")
            self.shakify.apply_rotation_shake(
                self.camera,
                duration_frames,
                intensity=shake_intensity,
                fps=fps
            )
            self.shakify.apply_location_shake(
                self.camera,
                duration_frames,
                intensity=0.003,
                fps=fps
            )
        else:
            print(f"\n🎲 Stage 6: Rotation shake désactivé")
        
        if apply_smart_crop and self.poi_heatmap:
            print(f"\n🎯 Stage 7: Application smart crop (sensor shift)")
            self.smart_crop.apply_sensor_shift(self.camera, self.poi_center)
        else:
            print(f"\n🎯 Stage 7: Smart crop désactivé")
        
        if apply_breathing:
            print(f"\n💨 Stage 8: Configuration breathing zoom")
            self.humanizer.add_breathing_zoom(self.camera, fps=fps)
        else:
            print(f"\n💨 Stage 8: Breathing zoom désactivé")
        
        print(f"\n📐 Stage 9: Configuration format de sortie")
        width, height = self.format_adapter.configure_render_resolution(output_format)
        
        source_ratio = 16/9
        target_ratio = width / height
        if target_ratio != source_ratio:
            print(f"\n🔍 Stage 10: Compensation FOV")
            self.format_adapter.compensate_fov(
                self.camera,
                source_ratio=source_ratio,
                target_ratio=target_ratio
            )
        else:
            print(f"\n🔍 Stage 10: Pas de compensation FOV nécessaire")
        
        print(f"\n📋 Stage 11: Intégration métadonnées")
        self._embed_metadata(
            scene_furnished_path,
            masterplan_path,
            output_format,
            duration_seconds,
            fps
        )
        
        print(f"\n💾 Stage 12: Sauvegarde scene_animated.blend")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"   ✅ Sauvegardé: {output_path}")
        
        total_time = time.time() - start_time
        
        camera_info = self.humanizer.get_camera_info(self.camera)
        render_info = self.format_adapter.get_render_info()
        
        result = {
            "status": "success",
            "project_id": self.project_id,
            "output_path": output_path,
            "scene_furnished_source": scene_furnished_path,
            "masterplan_source": masterplan_path,
            "camera_name": self.camera.name,
            "camera_focal_length": camera_info.get("focal_length"),
            "output_format": output_format,
            "resolution": f"{width}x{height}",
            "duration_seconds": duration_seconds,
            "duration_frames": duration_frames,
            "fps": fps,
            "poi_center": self.poi_center,
            "effects_applied": {
                "walking_bounce": apply_walking_bounce,
                "rotation_shake": apply_shake,
                "smart_crop": apply_smart_crop and bool(self.poi_heatmap),
                "breathing_zoom": apply_breathing
            },
            "processing_time_seconds": total_time,
            "exodus_version": self.EXODUS_VERSION,
            "generated_at": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ FRÉGATE DIRECTEUR PHOTO")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Caméra: {self.camera.name}")
        print(f"  Focale: {camera_info.get('focal_length', 'N/A')}mm")
        print(f"  Format: {output_format} ({width}x{height})")
        print(f"  Durée: {duration_seconds}s ({duration_frames} frames @ {fps}fps)")
        print(f"  POI center: ({self.poi_center[0]:.3f}, {self.poi_center[1]:.3f})")
        print(f"  Effets: bounce={apply_walking_bounce}, shake={apply_shake}, crop={apply_smart_crop}, breath={apply_breathing}")
        print(f"  Temps total: {total_time:.1f}s")
        print(f"  Output: {output_path}")
        print("=" * 60)
        
        return result


def run_directeur_pipeline(
    scene_furnished_path: Optional[str] = None,
    masterplan_path: Optional[str] = None,
    output_format: str = "VERTICAL",
    duration_seconds: float = 30.0,
    fps: int = 24,
    output_path: Optional[str] = None,
    project_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer le pipeline DIRECTEUR PHOTO.
    
    Compatible avec l'interface Colab / ligne de commande.
    
    Args:
        scene_furnished_path: Chemin vers scene_furnished.blend (F05)
        masterplan_path: Chemin vers masterplan.json
        output_format: Format de sortie (VERTICAL, HORIZONTAL, SQUARE)
        duration_seconds: Durée de l'animation
        fps: Frames par seconde
        output_path: Chemin de sortie scene_animated.blend
        project_id: ID du projet
        **kwargs: Arguments supplémentaires pour run()
        
    Returns:
        dict avec status et métadonnées
    """
    if project_id is None:
        if scene_furnished_path and os.path.exists(scene_furnished_path):
            project_id = Path(scene_furnished_path).parent.name
        else:
            project_id = "default_project"
    
    output_base = None
    if output_path:
        output_base = str(Path(output_path).parent.parent)
    
    pipeline = DirecteurPipeline(project_id, output_base)
    return pipeline.run(
        scene_furnished_path=scene_furnished_path,
        masterplan_path=masterplan_path,
        output_format=output_format,
        duration_seconds=duration_seconds,
        fps=fps,
        output_path=output_path,
        **kwargs
    )


if __name__ == "__main__":
    import sys
    
    print("=" * 50)
    print("🎬 DIRECTEUR PHOTO PIPELINE - Test Mode")
    print("=" * 50)
    
    if BPY_AVAILABLE:
        if len(sys.argv) > 1:
            scene_path = sys.argv[1]
            masterplan = sys.argv[2] if len(sys.argv) > 2 else None
            output = sys.argv[3] if len(sys.argv) > 3 else None
            output_fmt = sys.argv[4] if len(sys.argv) > 4 else "VERTICAL"
            
            result = run_directeur_pipeline(
                scene_furnished_path=scene_path,
                masterplan_path=masterplan,
                output_path=output,
                output_format=output_fmt
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Usage: blender --background --python directeur_pipeline.py -- scene_furnished.blend [masterplan.json] [output.blend] [format]")
    else:
        print(f"\n📦 Test configuration (sans Blender):")
        print(f"   F05_OUTPUT: {F05_OUTPUT}")
        print(f"   F06_OUTPUT: {F06_OUTPUT}")
        print(f"   F00_OUTPUT: {F00_OUTPUT}")
        print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
        
        print(f"\n🔧 Test imports:")
        humanizer = CameraHumanizer(verbose=False)
        shakify = Shakify(verbose=False)
        smart_crop = SmartCrop(verbose=False)
        format_adapter = FormatAdapter(verbose=False)
        print("   ✓ Toutes les classes instanciées")
        
    print("\n✅ Module directeur_pipeline.py fonctionnel")
