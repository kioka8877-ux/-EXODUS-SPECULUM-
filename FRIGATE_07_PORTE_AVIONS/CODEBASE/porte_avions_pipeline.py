#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate PORTE-AVIONS - Pipeline Orchestrateur
Pipeline final d'assemblage: Vidéo + Audio ASMR → Export multi-plateformes.

C'est ici que tous les flux convergent pour produire le livrable final.

Input: temp_render.mp4 ou frames_final/ (depuis F07) + audio config
Output: FINAL_SPECULUM_TOUR_4K.mp4 dans FRIGATE_08_PORTE_AVIONS/OUTPUT/

Philosophie: L'Immersion Sensorielle
Transformer une vidéo 3D en "vraie visite filmée à l'iPhone" via un sound design
ASMR qui renforce l'illusion de présence humaine.

Stages:
1. Synthèse audio ASMR (pas, room tone, froissements, respiration)
2. Mixage audio multi-pistes
3. Encodage vidéo + audio
4. Injection métadonnées anti-shadowban
5. Application variations anti-fingerprint
6. Export multi-plateformes

Usage:
    from FRIGATE_07_PORTE_AVIONS.CODEBASE.porte_avions_pipeline import run_porte_avions_pipeline
    
    result = run_porte_avions_pipeline(
        video_input="/path/to/temp_render.mp4",
        project_id="villa_monaco",
        export_platforms=["youtube_4k", "tiktok", "instagram_reels"]
    )
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from CORE_CONFIG.paths import (
        F06_OUTPUT, ASSETSHUB_PATH, DRIVE_ROOT
    )
    F07_OUTPUT = f"{DRIVE_ROOT}/FRIGATE_07_PORTE_AVIONS/OUTPUT/"
except ImportError:
    F06_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_06_ALCHIMISTE/OUTPUT/"
    F07_OUTPUT = "/content/drive/MyDrive/EXODUS-SPECULUM/FRIGATE_07_PORTE_AVIONS/OUTPUT/"
    ASSETSHUB_PATH = "/content/drive/MyDrive/EXODUS-SPECULUM/ASSETSHUB/"

from .ffmpeg_encoder import FFmpegEncoder, CODEC_PROFILES
from .asmr_synthesizer import (
    ASMRSynthesizer,
    SAMPLE_RATE,
    HANDHELD_Z_FREQ,
    HANDHELD_BREATHING_CYCLE
)
from .audio_mixer import AudioMixer
from .metadata_injector import MetadataInjector, ANTI_FINGERPRINT_PARAMS
from .format_exporter import FormatExporter, PLATFORM_SPECS

EXODUS_VERSION = "0.8.0"

ASMR_DEFAULTS = {
    "footsteps_volume": 0.5,
    "room_tone_volume": 0.3,
    "cloth_volume": 0.2,
    "breathing_volume": 0.15,
    "walking_freq_hz": HANDHELD_Z_FREQ,
    "breathing_cycle_sec": HANDHELD_BREATHING_CYCLE,
    "surface": "tile"
}


class PorteAvionsPipeline:
    """
    Pipeline final d'assemblage: Vidéo + Audio ASMR → Export multi-plateformes.
    
    C'est ici que tous les flux convergent pour produire le livrable final.
    Le Porte-Avions assemble les produits de toutes les frégates précédentes
    en une expérience immersive complète.
    
    Stages:
    1. Synthèse audio ASMR (synchronisé avec camera motion)
    2. Mixage audio multi-pistes
    3. Encodage vidéo + audio final
    4. Injection métadonnées (anti-shadowban)
    5. Anti-fingerprint variations
    6. Export multi-plateformes
    
    Usage:
        pipeline = PorteAvionsPipeline(
            project_id="villa_monaco",
            assetshub_path="/path/to/assetshub"
        )
        
        result = pipeline.run(
            video_input="/path/to/temp_render.mp4",
            export_platforms=["youtube_4k", "tiktok"]
        )
    """
    
    EXODUS_VERSION = EXODUS_VERSION
    
    def __init__(
        self,
        project_id: str,
        assetshub_path: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Args:
            project_id: Identifiant unique du projet
            assetshub_path: Chemin vers ASSETSHUB (pour samples audio)
            verbose: Affiche les logs détaillés
        """
        self.project_id = project_id
        self.assetshub_path = assetshub_path or ASSETSHUB_PATH
        self.verbose = verbose
        
        self.encoder = FFmpegEncoder(verbose=verbose)
        self.asmr = ASMRSynthesizer(self.assetshub_path, verbose=verbose)
        self.mixer = AudioMixer(verbose=verbose)
        self.metadata = MetadataInjector(verbose=verbose)
        self.exporter = FormatExporter(verbose=verbose)
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(message)
    
    def _print_banner(self) -> None:
        """Affiche la bannière de la frégate."""
        self._log("\n" + "=" * 60)
        self._log("🛫 FRÉGATE PORTE-AVIONS - ASSEMBLAGE FINAL")
        self._log(f"   Projet: {self.project_id}")
        self._log(f"   Version: {self.EXODUS_VERSION}")
        self._log("=" * 60)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Vérifie les dépendances du pipeline.
        
        Returns:
            Dict avec le status de chaque dépendance
        """
        deps = {
            "ffmpeg": self.encoder.check_ffmpeg(),
            "numpy": True,
            "scipy": self._check_scipy()
        }
        
        self._log("\n🔧 Dépendances:")
        for dep, status in deps.items():
            icon = "✓" if status else "✗"
            self._log(f"   {icon} {dep}")
        
        return deps
    
    def _check_scipy(self) -> bool:
        """Vérifie que scipy est disponible."""
        try:
            from scipy.io import wavfile
            return True
        except ImportError:
            return False
    
    def _get_video_duration(self, video_path: str) -> float:
        """Récupère la durée d'une vidéo via ffprobe."""
        info = self.encoder.get_video_info(video_path)
        return info.get("duration_sec", 30.0)
    
    def run(
        self,
        video_input: str,
        output_dir: Optional[str] = None,
        duration_sec: Optional[float] = None,
        generate_audio: bool = True,
        asmr_config: Optional[Dict[str, Any]] = None,
        apply_anti_fingerprint: bool = True,
        fingerprint_intensity: str = "subtle",
        export_platforms: Optional[List[str]] = None,
        codec_profile: str = "quality",
        smart_crop_poi: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Pipeline complet F08:
        1. Générer les pistes audio ASMR
        2. Mixer l'audio
        3. Encoder vidéo + audio
        4. Injecter métadonnées anti-shadowban
        5. Appliquer variations anti-fingerprint
        6. Exporter vers toutes les plateformes
        
        Args:
            video_input: temp_render.mp4 (depuis F07) ou dossier de frames
            output_dir: Dossier de sortie (défaut: F08_OUTPUT/project_id)
            duration_sec: Durée audio (défaut: détecté depuis vidéo)
            generate_audio: Générer le sound design ASMR
            asmr_config: Configuration ASMR personnalisée
            apply_anti_fingerprint: Appliquer les variations anti-fingerprint
            fingerprint_intensity: Intensité (subtle/moderate/aggressive)
            export_platforms: Plateformes cibles (défaut: None = pas d'export multi)
            codec_profile: Profil d'encodage (quality/compatibility/fast)
            smart_crop_poi: Point of Interest pour le crop vertical
            
        Returns:
            Dict avec les résultats du pipeline
        """
        start_time = time.time()
        
        self._print_banner()
        
        if output_dir is None:
            output_dir = str(Path(F08_OUTPUT) / self.project_id)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        self._log(f"\n📂 Chemins:")
        self._log(f"   Input: {video_input}")
        self._log(f"   Output: {output_dir}")
        
        deps = self.check_dependencies()
        
        if duration_sec is None:
            if video_input.endswith('.mp4') or video_input.endswith('.mov'):
                duration_sec = self._get_video_duration(video_input)
            else:
                duration_sec = 30.0
        
        self._log(f"\n⏱️ Durée détectée: {duration_sec:.1f}s")
        
        audio_path = None
        if generate_audio:
            self._log("\n🎵 Stage 1: Synthèse audio ASMR")
            
            config = {**ASMR_DEFAULTS, **(asmr_config or {})}
            
            footsteps = self.asmr.generate_footsteps_track(
                duration_sec,
                walking_freq_hz=config["walking_freq_hz"],
                surface=config["surface"]
            )
            self._log(f"   ✓ Pas générés (sync {config['walking_freq_hz']}Hz)")
            
            room_tone = self.asmr.generate_room_tone(duration_sec, style="villa")
            self._log("   ✓ Room tone villa")
            
            cloth = self.asmr.generate_cloth_rustle(duration_sec, intensity="subtle")
            self._log("   ✓ Froissements vêtements")
            
            breathing = self.asmr.generate_breathing(
                duration_sec,
                cycle_sec=config["breathing_cycle_sec"]
            )
            self._log(f"   ✓ Respiration subtile (cycle {config['breathing_cycle_sec']}s)")
            
            self._log("\n🎚️ Stage 2: Mixage audio")
            audio_path = f"{output_dir}/audio_asmr.wav"
            
            self.mixer.mix_tracks([
                (room_tone, config["room_tone_volume"]),
                (footsteps, config["footsteps_volume"]),
                (cloth, config["cloth_volume"]),
                (breathing, config["breathing_volume"])
            ], audio_path)
            
            self._log(f"   ✓ Mix exporté: {audio_path}")
        
        self._log("\n🎬 Stage 3: Encodage final")
        master_path = f"{output_dir}/master_4k60.mp4"
        
        if video_input.endswith('.mp4') or video_input.endswith('.mov'):
            self.encoder.encode_from_video(
                video_input,
                master_path,
                audio_path=audio_path,
                codec_profile=codec_profile
            )
        else:
            self.encoder.encode_from_frames(
                video_input,
                master_path,
                fps=60,
                codec_profile=codec_profile,
                audio_path=audio_path
            )
        
        self._log(f"   ✓ Master encodé: {master_path}")
        
        self._log("\n📋 Stage 4: Injection métadonnées")
        master_meta = f"{output_dir}/master_4k60_meta.mp4"
        self.metadata.inject_unique_metadata(
            master_path,
            master_meta,
            title=f"SPECULUM Tour - {self.project_id}"
        )
        
        final_path = f"{output_dir}/FINAL_SPECULUM_TOUR_4K.mp4"
        
        if apply_anti_fingerprint:
            self._log("\n🔒 Stage 5: Anti-fingerprint")
            self.metadata.apply_anti_fingerprint(
                master_meta,
                final_path,
                intensity=fingerprint_intensity
            )
        else:
            shutil.copy(master_meta, final_path)
            self._log(f"\n📄 Stage 5: Copie directe (anti-fingerprint désactivé)")
        
        self._log(f"   ✓ Final: {final_path}")
        
        exports = {}
        if export_platforms:
            self._log("\n📤 Stage 6: Export multi-plateformes")
            exports = self.exporter.export_all_platforms(
                final_path,
                output_dir,
                export_platforms,
                smart_crop_poi=smart_crop_poi
            )
        
        total_time = time.time() - start_time
        
        manifest = self._create_manifest(
            video_input, final_path, audio_path,
            exports, total_time, duration_sec
        )
        manifest_path = f"{output_dir}/porte_avions_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        self._print_summary(final_path, exports, total_time)
        
        return {
            "status": "success",
            "project_id": self.project_id,
            "final_video": final_path,
            "audio_path": audio_path,
            "exports": exports,
            "manifest_path": manifest_path,
            "processing_time_seconds": total_time,
            "exodus_version": self.EXODUS_VERSION
        }
    
    def _create_manifest(
        self,
        video_input: str,
        final_path: str,
        audio_path: Optional[str],
        exports: Dict[str, str],
        total_time: float,
        duration_sec: float
    ) -> Dict[str, Any]:
        """Crée le manifest JSON du traitement."""
        return {
            "exodus_version": self.EXODUS_VERSION,
            "frigate": "F08_PORTE_AVIONS",
            "project_id": self.project_id,
            "timestamp": datetime.now().isoformat(),
            "input": {
                "video": video_input,
                "duration_sec": duration_sec
            },
            "output": {
                "final_video": final_path,
                "audio": audio_path,
                "exports": exports
            },
            "processing": {
                "time_seconds": total_time,
                "stages_completed": 6,
                "platforms_exported": len(exports)
            },
            "asmr_config": ASMR_DEFAULTS
        }
    
    def _print_summary(
        self,
        final_path: str,
        exports: Dict[str, str],
        total_time: float
    ) -> None:
        """Affiche le résumé du traitement."""
        self._log("\n" + "=" * 60)
        self._log("🛫 RÉSUMÉ FRÉGATE PORTE-AVIONS")
        self._log("=" * 60)
        self._log(f"   Projet: {self.project_id}")
        self._log(f"   Output final: {final_path}")
        self._log(f"   Exports: {len(exports)}")
        for platform, path in exports.items():
            status = "✓" if not path.startswith("ERROR") else "✗"
            self._log(f"      {status} {platform}")
        self._log(f"   Temps total: {total_time:.1f}s ({total_time/60:.1f} min)")
        self._log("=" * 60)


def run_porte_avions_pipeline(
    video_input: Optional[str] = None,
    output_dir: Optional[str] = None,
    project_id: str = "default",
    generate_audio: bool = True,
    apply_anti_fingerprint: bool = True,
    export_platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fonction helper pour exécuter le pipeline Porte-Avions.
    
    Args:
        video_input: Chemin de la vidéo (défaut: F07_OUTPUT/temp_render.mp4)
        output_dir: Dossier de sortie (défaut: F08_OUTPUT/project_id)
        project_id: Identifiant du projet
        generate_audio: Générer le sound design ASMR
        apply_anti_fingerprint: Appliquer les variations anti-fingerprint
        export_platforms: Plateformes cibles pour export multi
        
    Returns:
        Dict avec les résultats du pipeline
    """
    if video_input is None:
        video_input = f"{F07_OUTPUT}temp_render.mp4"
    
    pipeline = PorteAvionsPipeline(project_id=project_id)
    
    return pipeline.run(
        video_input=video_input,
        output_dir=output_dir,
        generate_audio=generate_audio,
        apply_anti_fingerprint=apply_anti_fingerprint,
        export_platforms=export_platforms
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🛫 PORTE-AVIONS PIPELINE - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   EXODUS_VERSION: {EXODUS_VERSION}")
    print(f"   F07_OUTPUT: {F07_OUTPUT}")
    print(f"   F08_OUTPUT: {F08_OUTPUT}")
    print(f"   ASSETSHUB_PATH: {ASSETSHUB_PATH}")
    
    print(f"\n📋 ASMR Defaults:")
    for key, value in ASMR_DEFAULTS.items():
        print(f"   {key}: {value}")
    
    print(f"\n📋 Codec Profiles:")
    for name in CODEC_PROFILES.keys():
        print(f"   - {name}")
    
    print(f"\n📋 Plateformes d'export:")
    for platform in PLATFORM_SPECS.keys():
        print(f"   - {platform}")
    
    print(f"\n🔧 Test instanciation:")
    pipeline = PorteAvionsPipeline(project_id="test_project", verbose=False)
    print(f"   ✓ Pipeline créé")
    print(f"   ✓ Encoder: {pipeline.encoder is not None}")
    print(f"   ✓ ASMR: {pipeline.asmr is not None}")
    print(f"   ✓ Mixer: {pipeline.mixer is not None}")
    print(f"   ✓ Metadata: {pipeline.metadata is not None}")
    print(f"   ✓ Exporter: {pipeline.exporter is not None}")
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"\n🚀 Exécution pipeline:")
        result = run_porte_avions_pipeline(
            video_input=video_path,
            output_dir=output_dir,
            project_id="cli_run"
        )
        print(json.dumps(result, indent=2, default=str))
    else:
        print("\n📖 Usage:")
        print("   python porte_avions_pipeline.py <video.mp4> [output_dir]")
    
    print("\n✅ Module porte_avions_pipeline.py fonctionnel")
