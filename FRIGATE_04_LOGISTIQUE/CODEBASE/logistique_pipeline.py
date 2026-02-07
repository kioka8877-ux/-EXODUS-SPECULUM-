#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate LOGISTIQUE - Pipeline Orchestrateur
Remplace les Ghost Proxies par de vrais assets 3D linkés depuis ASSETSHUB.

Input: scene_projected.blend (depuis F04) + ASSETSHUB_PATH
Output: scene_furnished.blend avec assets réels linkés
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
        F03_OUTPUT, F04_OUTPUT,
        F04_CODEBASE, F04_INPUT,
        ASSETSHUB_PATH,
        PathConfig
    )
except ImportError:
    F03_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_03_PROJECTIONNISTE/OUTPUT/"
    F04_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_04_LOGISTIQUE/OUTPUT/"
    F04_INPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_04_LOGISTIQUE/INPUT/"
    F04_CODEBASE = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_04_LOGISTIQUE/"
    ASSETSHUB_PATH = "/content/drive/MyDrive/EXODUS-SPECULUM/ASSETSHUB/"
    PathConfig = None

from .ghost_detector import GhostDetector, GhostProxy
from .asset_matcher import AssetMatcher, AssetMatch
from .library_linker import LibraryLinker
from .lod_manager import LODManager


class LogistiquePipeline:
    """
    Pipeline complet de la Frégate LOGISTIQUE.
    
    Workflow:
    1. Charger scene_projected.blend (depuis F04-PROJECTIONNISTE)
    2. Détecter tous les ghost_proxies (custom property ghost_proxy=True)
    3. Pour chaque proxy: find_best_asset() → link_asset()
    4. Setup LOD drivers basés sur distance caméra
    5. Créer collection "ASSETS_LINKED", cacher collection "PROXIES"
    6. Intégrer métadonnées (assets_loaded, proxies_replaced, etc.)
    7. Sauvegarder scene_furnished.blend
    """
    
    EXODUS_VERSION = "0.5.0"
    DEFAULT_THRESHOLD = 0.7
    
    def __init__(self, project_id: str, output_base: Optional[str] = None):
        """
        Args:
            project_id: Identifiant unique du projet
            output_base: Dossier racine de sortie (défaut: F05_OUTPUT)
        """
        if not BPY_AVAILABLE:
            raise RuntimeError("🚫 Blender Python (bpy) not available. Run in Blender environment.")
        
        if output_base is None:
            output_base = F05_OUTPUT
        
        self.project_id = project_id
        self.output_dir = Path(output_base) / project_id
        
        self.ghost_detector = None
        self.asset_matcher = None
        self.library_linker = None
        self.lod_manager = None
        
        self.proxies: List[GhostProxy] = []
        self.matches: Dict[str, AssetMatch] = {}
        self.linked_assets: Dict[str, Any] = {}
        
        print(f"🚚 Logistique Pipeline initialisé")
        print(f"   Project ID: {project_id}")
        print(f"   Output: {self.output_dir}")
    
    def _find_scene_projected(self, scene_projected_path: Optional[str] = None) -> str:
        """Trouve le fichier scene_projected.blend."""
        if scene_projected_path and os.path.exists(scene_projected_path):
            return scene_projected_path
        
        search_paths = [
            Path(F04_OUTPUT) / self.project_id / "scene_projected.blend",
            Path(F05_INPUT) / self.project_id / "scene_projected.blend",
            Path(F05_INPUT) / "scene_projected.blend",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"🚫 scene_projected.blend non trouvé. Cherché dans: {[str(p) for p in search_paths]}"
        )
    
    def _find_assetshub(self, assetshub_path: Optional[str] = None) -> str:
        """Trouve le dossier ASSETSHUB."""
        if assetshub_path and os.path.exists(assetshub_path):
            return assetshub_path
        
        search_paths = [
            Path(ASSETSHUB_PATH),
            Path(F05_INPUT) / "ASSETSHUB",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            f"🚫 ASSETSHUB non trouvé. Cherché dans: {[str(p) for p in search_paths]}"
        )
    
    def _find_camera(self) -> Optional[Any]:
        """Trouve la caméra principale de la scène."""
        if bpy.context.scene.camera:
            return bpy.context.scene.camera
        
        cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        
        for cam in cameras:
            if "main" in cam.name.lower() or "projection" in cam.name.lower():
                return cam
        
        if cameras:
            return cameras[0]
        
        return None
    
    def _embed_metadata(
        self,
        scene_projected_path: str,
        assetshub_path: str
    ) -> None:
        """Intègre les métadonnées dans la scène."""
        scene = bpy.context.scene
        
        scene["exodus_version"] = self.EXODUS_VERSION
        scene["project_id"] = self.project_id
        scene["scene_projected_source"] = scene_projected_path
        scene["assetshub_source"] = assetshub_path
        scene["proxies_detected"] = len(self.proxies)
        scene["proxies_replaced"] = len(self.linked_assets)
        scene["assets_loaded"] = json.dumps(list(self.linked_assets.keys()))
        scene["generated_at"] = datetime.now().isoformat()
        scene["frigate"] = "F05_LOGISTIQUE"
        
        print("📋 Métadonnées intégrées")
    
    def run(
        self,
        scene_projected_path: Optional[str] = None,
        assetshub_path: Optional[str] = None,
        match_threshold: float = DEFAULT_THRESHOLD,
        setup_lod: bool = True,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute le pipeline complet F05-LOGISTIQUE.
        
        Args:
            scene_projected_path: Chemin vers scene_projected.blend (F04)
            assetshub_path: Chemin vers ASSETSHUB
            match_threshold: Seuil minimum de correspondance (0.0 à 1.0)
            setup_lod: Configure les drivers LOD
            output_path: Chemin de sortie scene_furnished.blend
            
        Returns:
            Dict avec status et métadonnées
        """
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("🚚 FRÉGATE LOGISTIQUE - GHOST PROXY → REAL ASSETS")
        print("=" * 60)
        
        scene_projected_path = self._find_scene_projected(scene_projected_path)
        assetshub_path = self._find_assetshub(assetshub_path)
        
        if output_path is None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(self.output_dir / "scene_furnished.blend")
        
        print(f"\n📂 Stage 1: Chargement scene_projected.blend")
        print(f"   Source: {scene_projected_path}")
        bpy.ops.wm.open_mainfile(filepath=scene_projected_path)
        
        print(f"\n👻 Stage 2: Détection des Ghost Proxies")
        self.ghost_detector = GhostDetector(verbose=True)
        self.proxies = self.ghost_detector.scan_scene()
        
        type_summary = self.ghost_detector.get_type_summary()
        print(f"   Types détectés: {type_summary}")
        
        if not self.proxies:
            print("   ⚠️ Aucun ghost proxy détecté - création de scène vide")
        
        print(f"\n🔍 Stage 3: Matching assets (threshold={match_threshold})")
        print(f"   ASSETSHUB: {assetshub_path}")
        self.asset_matcher = AssetMatcher(assetshub_path, verbose=True)
        
        for proxy in self.proxies:
            match = self.asset_matcher.find_best_asset(proxy, threshold=match_threshold)
            if match:
                self.matches[proxy.name] = match
        
        print(f"   ✓ {len(self.matches)}/{len(self.proxies)} proxies matchés")
        
        print(f"\n🔗 Stage 4: Linking assets")
        self.library_linker = LibraryLinker(verbose=True)
        
        for proxy in self.proxies:
            if proxy.name in self.matches:
                match = self.matches[proxy.name]
                linked_obj = self.library_linker.link_asset(match.asset_path, proxy)
                if linked_obj:
                    self.linked_assets[proxy.name] = linked_obj
        
        linker_stats = self.library_linker.get_stats()
        print(f"   ✓ Linked: {linker_stats['linked']}, Failed: {linker_stats['failed']}")
        
        self.library_linker.hide_proxies_collection()
        
        if setup_lod and self.linked_assets:
            print(f"\n📐 Stage 5: Configuration LOD drivers")
            self.lod_manager = LODManager(verbose=True)
            
            camera = self._find_camera()
            if camera:
                print(f"   Caméra: {camera.name}")
                lod_count = self.lod_manager.setup_lod_for_collection(
                    LibraryLinker.ASSETS_COLLECTION,
                    camera
                )
                print(f"   ✓ {lod_count} objets avec LOD configuré")
            else:
                print("   ⚠️ Aucune caméra trouvée - LOD non configuré")
        
        print(f"\n📋 Stage 6: Intégration métadonnées")
        self._embed_metadata(scene_projected_path, assetshub_path)
        
        print(f"\n💾 Stage 7: Sauvegarde scene_furnished.blend")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"   ✅ Sauvegardé: {output_path}")
        
        total_time = time.time() - start_time
        
        result = {
            "status": "success",
            "project_id": self.project_id,
            "output_path": output_path,
            "scene_projected_source": scene_projected_path,
            "assetshub_source": assetshub_path,
            "proxies_detected": len(self.proxies),
            "proxies_matched": len(self.matches),
            "assets_linked": len(self.linked_assets),
            "match_threshold": match_threshold,
            "lod_enabled": setup_lod,
            "type_summary": type_summary,
            "processing_time_seconds": total_time,
            "exodus_version": self.EXODUS_VERSION,
            "generated_at": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ FRÉGATE LOGISTIQUE")
        print("=" * 60)
        print(f"  Projet: {self.project_id}")
        print(f"  Proxies détectés: {len(self.proxies)}")
        print(f"  Proxies matchés: {len(self.matches)}")
        print(f"  Assets linkés: {len(self.linked_assets)}")
        print(f"  Temps total: {total_time:.1f}s")
        print(f"  Output: {output_path}")
        print("=" * 60)
        
        return result


def run_logistique_pipeline(
    scene_projected_path: Optional[str] = None,
    assetshub_path: Optional[str] = None,
    match_threshold: float = 0.7,
    setup_lod: bool = True,
    output_path: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour lancer le pipeline LOGISTIQUE.
    
    Compatible avec l'interface Colab / ligne de commande.
    
    Args:
        scene_projected_path: Chemin vers scene_projected.blend (F04)
        assetshub_path: Chemin vers ASSETSHUB
        match_threshold: Seuil minimum de correspondance
        setup_lod: Configure les drivers LOD
        output_path: Chemin de sortie scene_furnished.blend
        project_id: ID du projet (extrait de la scène si non fourni)
        
    Returns:
        dict avec status et métadonnées
    """
    if project_id is None:
        if scene_projected_path and os.path.exists(scene_projected_path):
            project_id = Path(scene_projected_path).parent.name
        else:
            project_id = "default_project"
    
    output_base = None
    if output_path:
        output_base = str(Path(output_path).parent.parent)
    
    pipeline = LogistiquePipeline(project_id, output_base)
    return pipeline.run(
        scene_projected_path=scene_projected_path,
        assetshub_path=assetshub_path,
        match_threshold=match_threshold,
        setup_lod=setup_lod,
        output_path=output_path
    )


if __name__ == "__main__":
    import sys
    
    print("=" * 50)
    print("🚚 LOGISTIQUE PIPELINE - Test Mode")
    print("=" * 50)
    
    if BPY_AVAILABLE:
        if len(sys.argv) > 1:
            scene_path = sys.argv[1]
            assetshub = sys.argv[2] if len(sys.argv) > 2 else None
            output = sys.argv[3] if len(sys.argv) > 3 else None
            
            result = run_logistique_pipeline(
                scene_projected_path=scene_path,
                assetshub_path=assetshub,
                output_path=output
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            print("Usage: blender --background --python logistique_pipeline.py -- scene_projected.blend [assetshub_path] [output.blend]")
    else:
        print(f"\n📦 Test configuration (sans Blender):")
        print(f"   F04_OUTPUT: {F04_OUTPUT}")
        print(f"   F05_OUTPUT: {F05_OUTPUT}")
        print(f"   ASSETSHUB_PATH: {ASSETSHUB_PATH}")
        print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
        
        print(f"\n🔧 Test classes:")
        detector = GhostDetector(verbose=False)
        matcher = AssetMatcher("/fake/path", verbose=False)
        linker = LibraryLinker(verbose=False)
        lod_mgr = LODManager(verbose=False)
        print("   ✓ Toutes les classes instanciées")
        
    print("\n✅ Module logistique_pipeline.py fonctionnel")
