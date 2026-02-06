#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate SCÉNOGRAPHE - Pipeline Complet
Orchestre la génération géométrique 3D via Blender Python.
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
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.config.paths import F03_INPUT, F03_OUTPUT, F00_OUTPUT, F01_OUTPUT, PathConfig
except ImportError:
    F03_INPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_SCENOGRAPHE/INPUT/"
    F03_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_SCENOGRAPHE/OUTPUT/"
    F00_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_00_CORTEX/OUTPUT/"
    F01_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_01_SCANNER/OUTPUT/"
    PathConfig = None

from .room_builder import RoomBuilder
from .proxy_generator import ProxyGenerator
from .opening_cutter import OpeningCutter


class ScenographePipeline:
    """
    Pipeline complet de la Frégate SCÉNOGRAPHE.
    
    Workflow:
    1. Charger masterplan.json (depuis F00-CORTEX)
    2. Reset Blender scene
    3. Créer collections organisées
    4. Construire la pièce (6 surfaces + displacement)
    5. Générer les proxies Ghost
    6. Percer les ouvertures
    7. Embed métadonnées
    8. Exporter scene_shell.blend
    """
    
    EXODUS_VERSION = "0.3.0"
    
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
        
        self.builder = None
        self.generator = None
        self.cutter = None
        
        self.surfaces = []
        self.proxies = []
        self.collections = {}
        
        print(f"🎭 Scénographe Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Output: {self.output_dir}")
    
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
    
    def _find_depth_maps_dir(self, depth_maps_dir: Optional[str] = None) -> str:
        """Trouve le dossier des depth maps."""
        if depth_maps_dir and os.path.exists(depth_maps_dir):
            return depth_maps_dir
        
        search_paths = [
            Path(F01_OUTPUT) / self.project_id / "depth_maps",
            Path(F03_INPUT) / self.project_id / "depth_maps",
            Path(F03_INPUT) / "depth_maps",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        print("⚠️ Dossier depth_maps non trouvé, displacement ignoré")
        return None
    
    def _reset_scene(self):
        """Reset complet de la scène Blender."""
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.length_unit = 'METERS'
        
        print("   🗑️ Scène reset")
    
    def _create_collections(self):
        """Crée les collections organisées."""
        room_collection = bpy.data.collections.new("ROOM_SHELL")
        proxy_collection = bpy.data.collections.new("PROXIES")
        
        bpy.context.scene.collection.children.link(room_collection)
        bpy.context.scene.collection.children.link(proxy_collection)
        
        self.collections = {
            "ROOM_SHELL": room_collection,
            "PROXIES": proxy_collection
        }
        
        print("   📁 Collections créées: ROOM_SHELL, PROXIES")
    
    def _move_to_collection(self, obj, collection_name: str):
        """Déplace un objet vers une collection spécifique."""
        target_collection = self.collections.get(collection_name)
        if not target_collection:
            return
        
        for col in obj.users_collection:
            col.objects.unlink(obj)
        
        target_collection.objects.link(obj)
    
    def _embed_metadata(self, masterplan_path: str, stats: Dict[str, Any]):
        """Intègre les métadonnées dans la scène."""
        scene = bpy.context.scene
        
        scene["exodus_version"] = self.EXODUS_VERSION
        scene["project_id"] = self.project_id
        scene["masterplan_source"] = masterplan_path
        scene["generated_at"] = datetime.now().isoformat()
        scene["surfaces_count"] = stats.get("surfaces_created", 0)
        scene["proxies_count"] = stats.get("proxies_created", 0)
        
        print("   📋 Métadonnées intégrées")
    
    def run(self,
            masterplan_path: Optional[str] = None,
            depth_maps_dir: Optional[str] = None,
            output_path: Optional[str] = None,
            apply_displacement: bool = True) -> Dict[str, Any]:
        """
        Exécute le pipeline complet F03-SCÉNOGRAPHE.
        
        Args:
            masterplan_path: Chemin vers masterplan.json
            depth_maps_dir: Dossier des depth maps
            output_path: Chemin de sortie scene_shell.blend
            apply_displacement: Appliquer le displacement (défaut: True)
            
        Returns:
            Dict avec status et métadonnées
        """
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("FRÉGATE SCÉNOGRAPHE - GÉNÉRATION GÉOMÉTRIE")
        print("=" * 60)
        
        masterplan_path = self._find_masterplan(masterplan_path)
        depth_maps_dir = self._find_depth_maps_dir(depth_maps_dir)
        
        if output_path is None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(self.output_dir / "scene_shell.blend")
        
        print(f"\n📄 Stage 1: Chargement masterplan")
        print(f"   Source: {masterplan_path}")
        
        with open(masterplan_path, 'r') as f:
            masterplan_data = json.load(f)
        
        masterplan = masterplan_data.get("masterplan", masterplan_data)
        
        dimensions = masterplan.get("dimensions_estimate", 
                                    masterplan.get("room", {}).get("dimensions", {}))
        furniture_list = masterplan.get("furniture", [])
        openings = masterplan.get("openings", [])
        
        print(f"   Dimensions: {dimensions}")
        print(f"   Meubles: {len(furniture_list)}")
        
        print(f"\n🗑️ Stage 2: Reset scène Blender")
        self._reset_scene()
        self._create_collections()
        
        print(f"\n🏗️ Stage 3: Construction de la pièce")
        self.builder = RoomBuilder(masterplan)
        self.surfaces = self.builder.create_room_shell()
        
        for surface in self.surfaces:
            self._move_to_collection(surface, "ROOM_SHELL")
        
        if apply_displacement and depth_maps_dir:
            print(f"\n📊 Stage 4: Application displacement")
            depth_files = sorted([
                f for f in os.listdir(depth_maps_dir)
                if f.endswith('.png')
            ])
            
            if depth_files:
                primary_depth = os.path.join(depth_maps_dir, depth_files[0])
                self.builder.apply_displacement(self.surfaces[0], primary_depth)
                print(f"   Depth map utilisée: {depth_files[0]}")
        else:
            print("\n⏭️ Stage 4: Displacement ignoré")
        
        print(f"\n🎭 Stage 5: Génération des proxies")
        self.generator = ProxyGenerator(dimensions)
        self.proxies = self.generator.generate_all_proxies(furniture_list)
        
        for proxy in self.proxies:
            self._move_to_collection(proxy, "PROXIES")
        
        print(f"\n✂️ Stage 6: Percement des ouvertures")
        if openings:
            self.cutter = OpeningCutter()
            walls_dict = {s.name: s for s in self.surfaces if "Wall" in s.name}
            self.cutter.cut_openings_from_masterplan(walls_dict, openings)
        else:
            print("   ℹ️ Aucune ouverture définie dans masterplan")
        
        stats = {
            "surfaces_created": len(self.surfaces),
            "proxies_created": len(self.proxies),
            "openings_created": len(openings)
        }
        
        print(f"\n📋 Stage 7: Intégration métadonnées")
        self._embed_metadata(masterplan_path, stats)
        
        print(f"\n💾 Stage 8: Sauvegarde scene_shell.blend")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"   ✅ Sauvegardé: {output_path}")
        
        total_time = time.time() - start_time
        
        result = {
            "status": "success",
            "project_id": self.project_id,
            "output_path": output_path,
            "masterplan_source": masterplan_path,
            "surfaces_created": len(self.surfaces),
            "proxies_created": len(self.proxies),
            "openings_created": len(openings),
            "processing_time_seconds": total_time,
            "exodus_version": self.EXODUS_VERSION,
            "generated_at": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ FRÉGATE SCÉNOGRAPHE")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Surfaces créées: {len(self.surfaces)}")
        print(f"  Proxies créés: {len(self.proxies)}")
        print(f"  Temps total: {total_time:.1f}s")
        print(f"  Output: {output_path}")
        print("=" * 60)
        
        return result


def run_scenographe_pipeline(
    masterplan_path: Optional[str] = None,
    depth_maps_dir: Optional[str] = None,
    output_path: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer le pipeline SCÉNOGRAPHE.
    
    Compatible avec l'interface définie dans la mission.
    
    Args:
        masterplan_path: Chemin vers masterplan.json
        depth_maps_dir: Dossier des depth maps
        output_path: Chemin de sortie scene_shell.blend
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
    
    pipeline = ScenographePipeline(project_id, output_base)
    return pipeline.run(
        masterplan_path=masterplan_path,
        depth_maps_dir=depth_maps_dir,
        output_path=output_path
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        masterplan = sys.argv[1]
        depth_dir = sys.argv[2] if len(sys.argv) > 2 else None
        output = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = run_scenographe_pipeline(
            masterplan_path=masterplan,
            depth_maps_dir=depth_dir,
            output_path=output
        )
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: blender --background --python scenographe_pipeline.py -- masterplan.json [depth_maps_dir] [output.blend]")
