#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PROJECTIONNISTE - Pipeline Complet
Orchestre le Camera Projection Mapping pour textures vidéo sur géométrie 3D.
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
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from CORE_CONFIG.paths import (
        F02_OUTPUT, F00_OUTPUT, F01_OUTPUT, 
        F03_CODEBASE, F03_INPUT, F03_OUTPUT,
        PathConfig
    )
except ImportError:
    F02_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_02_SCENOGRAPHE/OUTPUT/"
    F00_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_00_CORTEX/OUTPUT/"
    F01_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_01_SCANNER/OUTPUT/"
    F03_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_PROJECTIONNISTE/OUTPUT/"
    F03_INPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_PROJECTIONNISTE/INPUT/"
    F03_CODEBASE = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_PROJECTIONNISTE/"
    PathConfig = None

from .camera_setup import CameraSetup
from .uv_projector import UVProjector
from .multi_projection_shader import MultiProjectionShader


class ProjectionnistePipeline:
    """
    Pipeline complet de la Frégate PROJECTIONNISTE.
    
    Workflow:
    1. Charger scene_shell.blend (depuis F03-SCÉNOGRAPHE)
    2. Charger masterplan.json pour dimensions et type mouvement
    3. Sélectionner 3 keyframes (0%, 50%, 100%)
    4. Créer caméras de projection
    5. Projeter UVs sur les surfaces ROOM_SHELL
    6. Créer matériau multi-projection avec drivers
    7. Appliquer matériau aux surfaces
    8. Exporter scene_projected.blend
    """
    
    EXODUS_VERSION = "0.4.0"
    KEYFRAME_PERCENTS = [0, 50, 100]
    
    def __init__(self, project_id: str, output_base: Optional[str] = None):
        """
        Args:
            project_id: Identifiant unique du projet
            output_base: Dossier racine de sortie (défaut: F03_OUTPUT)
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("Blender Python (bpy) not available. Run in Blender environment.")
        
        if output_base is None:
            output_base = F03_OUTPUT
        
        self.project_id = project_id
        self.output_dir = Path(output_base) / project_id
        
        self.camera_setup = None
        self.uv_projector = None
        self.shader_builder = None
        
        self.cameras = []
        self.surfaces = []
        self.keyframe_paths = []
        
        print(f"🎬 Projectionniste Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Output: {self.output_dir}")
    
    def _find_scene_shell(self, scene_shell_path: Optional[str] = None) -> str:
        """Trouve le fichier scene_shell.blend."""
        if scene_shell_path and os.path.exists(scene_shell_path):
            return scene_shell_path
        
        search_paths = [
            Path(F03_OUTPUT) / self.project_id / "scene_shell.blend",
            Path(F03_INPUT) / self.project_id / "scene_shell.blend",
            Path(F03_INPUT) / "scene_shell.blend",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"scene_shell.blend non trouvé. Cherché dans: {search_paths}"
        )
    
    def _find_masterplan(self, masterplan_path: Optional[str] = None) -> str:
        """Trouve le fichier masterplan.json."""
        if masterplan_path and os.path.exists(masterplan_path):
            return masterplan_path
        
        search_paths = [
            Path(F00_OUTPUT) / self.project_id / "masterplan.json",
            Path(F03_INPUT) / self.project_id / "masterplan.json",
            Path(F03_INPUT) / "masterplan.json",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"masterplan.json non trouvé. Cherché dans: {search_paths}"
        )
    
    def _find_frames_dir(self, frames_dir: Optional[str] = None) -> str:
        """Trouve le dossier des frames extraites."""
        if frames_dir and os.path.exists(frames_dir):
            return frames_dir
        
        search_paths = [
            Path(F01_OUTPUT) / self.project_id / "frames",
            Path(F03_INPUT) / self.project_id / "frames",
            Path(F03_INPUT) / "frames",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"Dossier frames/ non trouvé. Cherché dans: {search_paths}"
        )
    
    def _select_keyframes(self, frames_dir: str) -> List[str]:
        """
        Sélectionne 3 keyframes (0%, 50%, 100%) depuis le dossier frames.
        
        Returns:
            Liste de 3 chemins vers les images keyframe
        """
        frames = sorted([
            f for f in os.listdir(frames_dir) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        
        if len(frames) < 3:
            raise ValueError(f"Besoin d'au moins 3 frames, trouvé: {len(frames)}")
        
        indices = [
            0,
            len(frames) // 2,
            len(frames) - 1
        ]
        
        keyframe_paths = [os.path.join(frames_dir, frames[i]) for i in indices]
        
        print(f"   🎞️ Keyframes sélectionnées:")
        for i, path in enumerate(keyframe_paths):
            print(f"      {self.KEYFRAME_PERCENTS[i]}%: {os.path.basename(path)}")
        
        return keyframe_paths
    
    def _get_room_shell_objects(self) -> List:
        """Récupère les objets mesh de la collection ROOM_SHELL."""
        room_shell = bpy.data.collections.get("ROOM_SHELL")
        
        if not room_shell:
            raise ValueError("Collection ROOM_SHELL non trouvée dans scene_shell.blend")
        
        surfaces = [obj for obj in room_shell.objects if obj.type == 'MESH']
        
        if not surfaces:
            raise ValueError("Aucun objet mesh trouvé dans ROOM_SHELL")
        
        print(f"   🏛️ {len(surfaces)} surfaces trouvées dans ROOM_SHELL")
        return surfaces
    
    def _embed_metadata(self, masterplan_path: str, frames_dir: str):
        """Intègre les métadonnées dans la scène."""
        scene = bpy.context.scene
        
        scene["exodus_version"] = self.EXODUS_VERSION
        scene["project_id"] = self.project_id
        scene["projection_source"] = frames_dir
        scene["masterplan_source"] = masterplan_path
        scene["keyframes_used"] = json.dumps(self.keyframe_paths)
        scene["generated_at"] = datetime.now().isoformat()
        scene["cameras_created"] = len(self.cameras)
        scene["surfaces_projected"] = len(self.surfaces)
        
        print("   📋 Métadonnées intégrées")
    
    def run(
        self,
        scene_shell_path: Optional[str] = None,
        masterplan_path: Optional[str] = None,
        frames_dir: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute le pipeline complet F04-PROJECTIONNISTE.
        
        Args:
            scene_shell_path: Chemin vers scene_shell.blend (F03)
            masterplan_path: Chemin vers masterplan.json (F00/F02)
            frames_dir: Dossier des frames extraites (F01)
            output_path: Chemin de sortie scene_projected.blend
            
        Returns:
            Dict avec status et métadonnées
        """
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("FRÉGATE PROJECTIONNISTE - CAMERA PROJECTION MAPPING")
        print("=" * 60)
        
        scene_shell_path = self._find_scene_shell(scene_shell_path)
        masterplan_path = self._find_masterplan(masterplan_path)
        frames_dir = self._find_frames_dir(frames_dir)
        
        if output_path is None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(self.output_dir / "scene_projected.blend")
        
        print(f"\n📂 Stage 1: Chargement scene_shell.blend")
        print(f"   Source: {scene_shell_path}")
        bpy.ops.wm.open_mainfile(filepath=scene_shell_path)
        
        print(f"\n📄 Stage 2: Chargement masterplan.json")
        print(f"   Source: {masterplan_path}")
        with open(masterplan_path, 'r') as f:
            masterplan_data = json.load(f)
        
        masterplan = masterplan_data.get("masterplan", masterplan_data)
        dimensions = masterplan.get("dimensions_estimate", 
                                   masterplan.get("room", {}).get("dimensions", {}))
        movement_type = masterplan.get("camera_movement_type", "linear_forward")
        
        print(f"   Dimensions: {dimensions}")
        print(f"   Movement: {movement_type}")
        
        print(f"\n🎞️ Stage 3: Sélection des keyframes")
        self.keyframe_paths = self._select_keyframes(frames_dir)
        
        print(f"\n📷 Stage 4: Création des caméras de projection")
        self.camera_setup = CameraSetup(dimensions)
        positions = self.camera_setup.estimate_camera_path(movement_type)
        self.cameras = self.camera_setup.create_projection_cameras(positions)
        cam_collection = self.camera_setup.create_camera_collection(self.cameras)
        
        print(f"\n🏛️ Stage 5: Identification des surfaces")
        self.surfaces = self._get_room_shell_objects()
        
        print(f"\n📐 Stage 6: Projection UV multi-keyframes")
        self.uv_projector = UVProjector()
        uv_results = self.uv_projector.project_all_keyframes(
            self.surfaces, 
            self.cameras,
            use_blender_op=False
        )
        
        print(f"\n🎨 Stage 7: Construction shader multi-projection")
        self.shader_builder = MultiProjectionShader()
        material = self.shader_builder.build_complete_shader(
            keyframe_paths=self.keyframe_paths,
            driver_object=self.cameras[0],
            add_feathering=True
        )
        
        print(f"\n🖌️ Stage 8: Application du matériau")
        self.shader_builder.apply_to_objects(self.surfaces, material)
        
        print(f"\n📋 Stage 9: Intégration métadonnées")
        self._embed_metadata(masterplan_path, frames_dir)
        
        print(f"\n💾 Stage 10: Sauvegarde scene_projected.blend")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"   ✅ Sauvegardé: {output_path}")
        
        total_time = time.time() - start_time
        
        result = {
            "status": "success",
            "project_id": self.project_id,
            "output_path": output_path,
            "scene_shell_source": scene_shell_path,
            "masterplan_source": masterplan_path,
            "frames_source": frames_dir,
            "cameras_created": len(self.cameras),
            "surfaces_projected": len(self.surfaces),
            "keyframes_used": self.keyframe_paths,
            "uv_layers_per_surface": 3,
            "material_name": material.name,
            "processing_time_seconds": total_time,
            "exodus_version": self.EXODUS_VERSION,
            "generated_at": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ FRÉGATE PROJECTIONNISTE")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Caméras créées: {len(self.cameras)}")
        print(f"  Surfaces projetées: {len(self.surfaces)}")
        print(f"  UV layers par surface: 3")
        print(f"  Temps total: {total_time:.1f}s")
        print(f"  Output: {output_path}")
        print("=" * 60)
        
        return result


def run_projectionniste_pipeline(
    scene_shell_path: Optional[str] = None,
    frames_dir: Optional[str] = None,
    masterplan_path: Optional[str] = None,
    output_path: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer le pipeline PROJECTIONNISTE.
    
    Compatible avec l'interface définie dans la mission.
    
    Args:
        scene_shell_path: Chemin vers scene_shell.blend (F03)
        frames_dir: Dossier des frames extraites (F01)
        masterplan_path: Chemin vers masterplan.json (F02)
        output_path: Chemin de sortie scene_projected.blend
        project_id: ID du projet (extrait du masterplan si non fourni)
        
    Returns:
        dict avec status et métadonnées
    """
    if project_id is None:
        if masterplan_path and os.path.exists(masterplan_path):
            with open(masterplan_path, 'r') as f:
                data = json.load(f)
                project_id = data.get("project_id", "default_project")
        else:
            project_id = "default_project"
    
    output_base = None
    if output_path:
        output_base = str(Path(output_path).parent.parent)
    
    pipeline = ProjectionnistePipeline(project_id, output_base)
    return pipeline.run(
        scene_shell_path=scene_shell_path,
        masterplan_path=masterplan_path,
        frames_dir=frames_dir,
        output_path=output_path
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        scene_shell = sys.argv[1]
        frames = sys.argv[2] if len(sys.argv) > 2 else None
        masterplan = sys.argv[3] if len(sys.argv) > 3 else None
        output = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = run_projectionniste_pipeline(
            scene_shell_path=scene_shell,
            frames_dir=frames,
            masterplan_path=masterplan,
            output_path=output
        )
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: blender --background --python projectionniste_pipeline.py -- scene_shell.blend [frames_dir] [masterplan.json] [output.blend]")
