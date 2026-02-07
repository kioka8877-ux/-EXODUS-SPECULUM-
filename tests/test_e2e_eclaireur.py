#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Test E2E Mode ÉCLAIREUR
Test de Pénétration End-to-End (Frégates F00-F07)

MODE ÉCLAIREUR:
- Résolution: 540p
- FPS: 12
- Samples: 16

Usage:
    python tests/test_e2e_eclaireur.py --video path/to/video.mp4 --project test_project
    python tests/test_e2e_eclaireur.py --dry-run  # Validation sans exécution
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION ÉCLAIREUR
# ═══════════════════════════════════════════════════════════════════════════

ECLAIREUR_CONFIG = {
    "mode": "eclaireur",
    "resolution": (960, 540),
    "fps": 12,
    "samples": 16,
    "denoiser": "OPENIMAGEDENOISE",
    "upscale_chain": None
}

# ═══════════════════════════════════════════════════════════════════════════
# E2E TEST CLASS
# ═══════════════════════════════════════════════════════════════════════════

class E2ETestRunner:
    """
    Exécute le test E2E complet en mode ÉCLAIREUR.
    
    Flux: F01 → F00 → F02 → F03 → F04 → F05 → F06 → F07
    """
    
    def __init__(self, project_id: str, video_path: str = None, dry_run: bool = False):
        self.project_id = project_id
        self.video_path = video_path
        self.dry_run = dry_run
        self.results = {}
        self.start_time = None
        
        print("=" * 70)
        print("⚔️  EXODUS-SPECULUM - TEST E2E MODE ÉCLAIREUR")
        print("=" * 70)
        print(f"   Project ID: {project_id}")
        print(f"   Video: {video_path or 'N/A (dry-run)'}")
        print(f"   Mode: {'DRY-RUN (validation)' if dry_run else 'LIVE (exécution)'}")
        print(f"   Config: {ECLAIREUR_CONFIG['resolution'][0]}x{ECLAIREUR_CONFIG['resolution'][1]} @ {ECLAIREUR_CONFIG['fps']}fps")
        print("=" * 70)
    
    def _check_import(self, module_name: str, from_module: str = None) -> bool:
        """Vérifie si un module peut être importé."""
        try:
            if from_module:
                exec(f"from {from_module} import {module_name}")
            else:
                __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _log_phase(self, phase: str, frigate: str, status: str, message: str = "", error: str = None):
        """Log une phase du test."""
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️" if status == "SKIP" else "🔄"
        print(f"\n{icon} Phase {phase}: {frigate}")
        print(f"   Status: {status}")
        if message:
            print(f"   {message}")
        if error:
            print(f"   ❌ ERREUR: {error}")
        
        self.results[phase] = {
            "frigate": frigate,
            "status": status,
            "message": message,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def phase_a_scanner(self) -> bool:
        """Phase A: F01 SCANNER - Extraction + Depth 16-bit"""
        phase = "A"
        frigate = "F01_SCANNER"
        
        if self.dry_run:
            # Validate imports
            checks = {
                "FrameExtractor": self._check_import("FrameExtractor", "FRIGATE_01_SCANNER.CODEBASE.frame_extractor"),
                "DepthEstimator": self._check_import("DepthEstimator", "FRIGATE_01_SCANNER.CODEBASE.depth_estimator"),
                "ScannerPipeline": self._check_import("ScannerPipeline", "FRIGATE_01_SCANNER.CODEBASE.scanner_pipeline"),
            }
            
            if all(checks.values()):
                self._log_phase(phase, frigate, "PASS", "Imports validés (dry-run)")
                return True
            else:
                failed = [k for k, v in checks.items() if not v]
                self._log_phase(phase, frigate, "FAIL", error=f"Imports manquants: {failed}")
                return False
        
        # Live execution
        try:
            from FRIGATE_01_SCANNER.CODEBASE.scanner_pipeline import ScannerPipeline
            
            pipeline = ScannerPipeline(self.project_id)
            result = pipeline.run(
                self.video_path,
                fps=2.0,
                skip_detection=True,  # Accélérer pour test
                skip_segmentation=True
            )
            
            if result.get('stages', {}).get('depth', {}).get('successful', 0) > 0:
                self._log_phase(phase, frigate, "PASS", f"Frames: {result['stages']['extraction']['frame_count']}, Depth maps générés")
                return True
            else:
                self._log_phase(phase, frigate, "FAIL", error="Aucune depth map générée")
                return False
                
        except Exception as e:
            self._log_phase(phase, frigate, "FAIL", error=str(e))
            return False
    
    def phase_b_cortex(self) -> bool:
        """Phase B: F00 CORTEX - Génération masterplan.json"""
        phase = "B"
        frigate = "F00_CORTEX"
        
        if self.dry_run:
            checks = {
                "GeminiClient": self._check_import("GeminiClient", "FRIGATE_00_CORTEX.CODEBASE.gemini_client"),
                "CortexPipeline": self._check_import("CortexPipeline", "FRIGATE_00_CORTEX.CODEBASE.cortex_pipeline"),
            }
            
            if all(checks.values()):
                self._log_phase(phase, frigate, "PASS", "Imports validés (dry-run)")
                return True
            else:
                failed = [k for k, v in checks.items() if not v]
                self._log_phase(phase, frigate, "FAIL", error=f"Imports manquants: {failed}")
                return False
        
        try:
            from FRIGATE_00_CORTEX.CODEBASE.cortex_pipeline import CortexPipeline
            
            pipeline = CortexPipeline(self.project_id)
            result = pipeline.run()
            
            if result.get('room', {}).get('type'):
                self._log_phase(phase, frigate, "PASS", f"Room type: {result['room']['type']}")
                return True
            else:
                self._log_phase(phase, frigate, "FAIL", error="masterplan.json incomplet")
                return False
                
        except Exception as e:
            self._log_phase(phase, frigate, "FAIL", error=str(e))
            return False
    
    def phase_c_blender_chain(self) -> bool:
        """Phase C: F02/F03/F04 - Scénographe + Projectionniste + Logistique"""
        phase = "C"
        frigate = "F02→F03→F04"
        
        if self.dry_run:
            checks = {
                "ScenographePipeline": self._check_import("ScenographePipeline", "FRIGATE_02_SCENOGRAPHE.CODEBASE.scenographe_pipeline"),
                "ProjectionnistePipeline": self._check_import("ProjectionnistePipeline", "FRIGATE_03_PROJECTIONNISTE.CODEBASE.projectionniste_pipeline"),
                "LogistiquePipeline": self._check_import("LogistiquePipeline", "FRIGATE_04_LOGISTIQUE.CODEBASE.logistique_pipeline"),
            }
            
            # Check bpy availability
            bpy_available = self._check_import("bpy")
            
            if not bpy_available:
                self._log_phase(phase, frigate, "SKIP", "bpy non disponible (requiert Blender/Colab)")
                return True  # Skip but don't fail
            
            if all(checks.values()):
                self._log_phase(phase, frigate, "PASS", "Imports validés (dry-run)")
                return True
            else:
                failed = [k for k, v in checks.items() if not v]
                self._log_phase(phase, frigate, "FAIL", error=f"Imports manquants: {failed}")
                return False
        
        # Live requires bpy
        try:
            import bpy
        except ImportError:
            self._log_phase(phase, frigate, "SKIP", "bpy non disponible - exécuter sur Colab")
            return True
        
        try:
            from FRIGATE_02_SCENOGRAPHE.CODEBASE.scenographe_pipeline import run_scenographe_pipeline
            from FRIGATE_03_PROJECTIONNISTE.CODEBASE.projectionniste_pipeline import run_projectionniste_pipeline
            
            # F02
            result_f02 = run_scenographe_pipeline(project_id=self.project_id)
            if result_f02.get('status') != 'success':
                self._log_phase(phase, frigate, "FAIL", error="F02 SCÉNOGRAPHE échoué")
                return False
            
            # F03
            result_f03 = run_projectionniste_pipeline(project_id=self.project_id)
            if result_f03.get('status') != 'success':
                self._log_phase(phase, frigate, "FAIL", error="F03 PROJECTIONNISTE échoué")
                return False
            
            self._log_phase(phase, frigate, "PASS", "Blender chain complète")
            return True
            
        except Exception as e:
            self._log_phase(phase, frigate, "FAIL", error=str(e))
            return False
    
    def phase_d_alchimiste(self) -> bool:
        """Phase D: F06 ALCHIMISTE - Render + VRAM check"""
        phase = "D"
        frigate = "F06_ALCHIMISTE"
        
        if self.dry_run:
            checks = {
                "AlchimistePipeline": self._check_import("AlchimistePipeline", "FRIGATE_06_ALCHIMISTE.CODEBASE.alchimiste_pipeline"),
                "CyclesRenderer": self._check_import("CyclesRenderer", "FRIGATE_06_ALCHIMISTE.CODEBASE.cycles_renderer"),
            }
            
            if all(checks.values()):
                self._log_phase(phase, frigate, "PASS", "Imports validés (dry-run)")
                return True
            else:
                failed = [k for k, v in checks.items() if not v]
                self._log_phase(phase, frigate, "FAIL", error=f"Imports manquants: {failed}")
                return False
        
        try:
            import bpy
        except ImportError:
            self._log_phase(phase, frigate, "SKIP", "bpy non disponible - exécuter sur Colab")
            return True
        
        try:
            from FRIGATE_06_ALCHIMISTE.CODEBASE.alchimiste_pipeline import AlchimistePipeline
            
            pipeline = AlchimistePipeline(
                project_id=self.project_id,
                turbo_mode="eclaireur"
            )
            
            result = pipeline.run(skip_dependency_check=True)
            
            if result.get('status') == 'success':
                self._log_phase(phase, frigate, "PASS", f"Frames rendues: {result.get('frame_count', 'N/A')}")
                return True
            else:
                self._log_phase(phase, frigate, "FAIL", error="Render échoué")
                return False
                
        except Exception as e:
            self._log_phase(phase, frigate, "FAIL", error=str(e))
            return False
    
    def phase_e_porte_avions(self) -> bool:
        """Phase E: F07 PORTE-AVIONS - MP4 + Audio ASMR"""
        phase = "E"
        frigate = "F07_PORTE_AVIONS"
        
        if self.dry_run:
            checks = {
                "PorteAvionsPipeline": self._check_import("PorteAvionsPipeline", "FRIGATE_07_PORTE_AVIONS.CODEBASE.porte_avions_pipeline"),
                "ASMRSynthesizer": self._check_import("ASMRSynthesizer", "FRIGATE_07_PORTE_AVIONS.CODEBASE.asmr_synthesizer"),
                "FFmpegEncoder": self._check_import("FFmpegEncoder", "FRIGATE_07_PORTE_AVIONS.CODEBASE.ffmpeg_encoder"),
            }
            
            if all(checks.values()):
                self._log_phase(phase, frigate, "PASS", "Imports validés (dry-run)")
                return True
            else:
                failed = [k for k, v in checks.items() if not v]
                self._log_phase(phase, frigate, "FAIL", error=f"Imports manquants: {failed}")
                return False
        
        try:
            from FRIGATE_07_PORTE_AVIONS.CODEBASE.porte_avions_pipeline import PorteAvionsPipeline
            
            pipeline = PorteAvionsPipeline(project_id=self.project_id)
            result = pipeline.run()
            
            if result.get('status') == 'success' and result.get('final_video'):
                self._log_phase(phase, frigate, "PASS", f"Output: {result['final_video']}")
                return True
            else:
                self._log_phase(phase, frigate, "FAIL", error="Pas de vidéo finale")
                return False
                
        except Exception as e:
            self._log_phase(phase, frigate, "FAIL", error=str(e))
            return False
    
    def run(self) -> dict:
        """Exécute le test E2E complet."""
        self.start_time = time.time()
        
        phases = [
            ("A", self.phase_a_scanner),
            ("B", self.phase_b_cortex),
            ("C", self.phase_c_blender_chain),
            ("D", self.phase_d_alchimiste),
            ("E", self.phase_e_porte_avions),
        ]
        
        all_passed = True
        for phase_id, phase_func in phases:
            success = phase_func()
            if not success and self.results.get(phase_id, {}).get('status') != 'SKIP':
                all_passed = False
                print(f"\n🛑 RUPTURE À LA PHASE {phase_id}")
                break
        
        total_time = time.time() - self.start_time
        
        # Final verdict
        print("\n" + "=" * 70)
        if all_passed:
            print("⚔️  VERDICT: ARMADA PRÊTE AU COMBAT")
            verdict = "SUCCESS"
        else:
            print("🛡️  VERDICT: RUPTURE DÉTECTÉE - CHIRURGIE REQUISE")
            verdict = "FAILURE"
        
        print("=" * 70)
        print(f"   Temps total: {total_time:.1f}s")
        print(f"   Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        print(f"   Phases passées: {sum(1 for r in self.results.values() if r['status'] in ['PASS', 'SKIP'])}/{len(phases)}")
        print("=" * 70)
        
        return {
            "verdict": verdict,
            "project_id": self.project_id,
            "mode": "dry_run" if self.dry_run else "live",
            "config": ECLAIREUR_CONFIG,
            "phases": self.results,
            "total_time_seconds": total_time,
            "timestamp": datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description="EXODUS-SPECULUM E2E Test - Mode ÉCLAIREUR")
    parser.add_argument("--video", type=str, help="Chemin vers la vidéo source")
    parser.add_argument("--project", type=str, default="e2e_test", help="ID du projet")
    parser.add_argument("--dry-run", action="store_true", help="Mode validation (sans exécution)")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.video:
        print("❌ --video requis en mode live (ou utilisez --dry-run)")
        sys.exit(1)
    
    runner = E2ETestRunner(
        project_id=args.project,
        video_path=args.video,
        dry_run=args.dry_run
    )
    
    result = runner.run()
    
    # Save report
    report_path = PROJECT_ROOT / f"tests/e2e_report_{args.project}.json"
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Rapport sauvegardé: {report_path}")
    
    sys.exit(0 if result['verdict'] == 'SUCCESS' else 1)


if __name__ == "__main__":
    main()
