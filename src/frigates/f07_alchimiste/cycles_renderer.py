#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate ALCHIMISTE - Cycles Renderer
Configuration et rendu Blender Cycles optimisé GPU (T4 Colab).

Utilise OptiX denoiser pour qualité maximale avec samples réduits.
Supporte les trois modes TURBO-SPECULUM: ÉCLAIREUR, CONQUÉRANT, SOUVERAIN.
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None

TURBO_MODES = {
    "eclaireur": {
        "render_resolution": (960, 540),
        "samples": 16,
        "fps": 12,
        "denoiser": "OPENIMAGEDENOISE",
        "upscale_chain": None,
        "final_resolution": (960, 540),
        "final_fps": 12
    },
    "conquerant": {
        "render_resolution": (1920, 1080),
        "samples": 32,
        "fps": 24,
        "denoiser": "OPTIX",
        "upscale_chain": ["ESRGAN_4X", "RIFE_2.5X"],
        "final_resolution": (3840, 2160),
        "final_fps": 60
    },
    "souverain": {
        "render_resolution": (3840, 2160),
        "samples": 128,
        "fps": 60,
        "denoiser": "OPTIX",
        "upscale_chain": None,
        "final_resolution": (3840, 2160),
        "final_fps": 60
    }
}


class CyclesRenderer:
    """
    Configure Cycles pour rendu optimisé GPU (T4 Colab).
    Utilise OptiX denoiser pour qualité maximale avec samples réduits.
    
    Modes TURBO-SPECULUM:
    - ÉCLAIREUR: 540p/16 samples/12fps (preview rapide)
    - CONQUÉRANT: 1080p/32 samples/24fps (base pour upscale)
    - SOUVERAIN: 4K/128 samples/60fps (rendu natif premium)
    
    Usage:
        renderer = CyclesRenderer(turbo_mode="conquerant")
        renderer.configure_cycles()
        frames = renderer.render_frame_range(output_dir, 1, 100)
    """
    
    def __init__(self, turbo_mode: str = "conquerant", verbose: bool = True):
        """
        Args:
            turbo_mode: Mode TURBO-SPECULUM (eclaireur/conquerant/souverain)
            verbose: Affiche les logs
        """
        if turbo_mode not in TURBO_MODES:
            raise ValueError(f"Mode inconnu: {turbo_mode}. Valides: {list(TURBO_MODES.keys())}")
        
        self.mode = turbo_mode
        self.config = TURBO_MODES[turbo_mode]
        self.verbose = verbose
        
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"⚗️ [CyclesRenderer] {message}")
    
    def configure_cycles(self) -> Dict[str, Any]:
        """
        Configure Cycles selon le TURBO_MODE.
        
        Returns:
            Dict avec les paramètres appliqués
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - configuration simulée")
            return {"status": "simulated", "mode": self.mode, **self.config}
        
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        
        scene.cycles.device = 'GPU'
        prefs = bpy.context.preferences.addons['cycles'].preferences
        
        try:
            prefs.compute_device_type = 'OPTIX'
            self._log("GPU: OptiX activé")
        except Exception:
            try:
                prefs.compute_device_type = 'CUDA'
                self._log("GPU: CUDA activé (OptiX non disponible)")
            except Exception:
                prefs.compute_device_type = 'NONE'
                self._log("⚠️ GPU non disponible - rendu CPU")
        
        prefs.get_devices()
        for device in prefs.devices:
            device.use = True
            self._log(f"  Device activé: {device.name}")
        
        scene.cycles.samples = self.config['samples']
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.adaptive_min_samples = max(1, self.config['samples'] // 4)
        
        scene.cycles.use_denoising = True
        try:
            scene.cycles.denoiser = self.config['denoiser']
            self._log(f"Denoiser: {self.config['denoiser']}")
        except Exception:
            scene.cycles.denoiser = 'OPENIMAGEDENOISE'
            self._log("Denoiser: OIDN (fallback)")
        
        res = self.config['render_resolution']
        scene.render.resolution_x = res[0]
        scene.render.resolution_y = res[1]
        scene.render.resolution_percentage = 100
        
        scene.render.fps = self.config['fps']
        scene.render.fps_base = 1.0
        
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 15
        
        scene.cycles.max_bounces = 8
        scene.cycles.diffuse_bounces = 4
        scene.cycles.glossy_bounces = 4
        scene.cycles.transmission_bounces = 8
        scene.cycles.volume_bounces = 2
        scene.cycles.transparent_max_bounces = 8
        
        scene.render.use_persistent_data = True
        
        self._log(f"✓ Cycles configuré - Mode {self.mode.upper()}")
        self._log(f"  Résolution: {res[0]}x{res[1]}")
        self._log(f"  Samples: {self.config['samples']}")
        self._log(f"  FPS: {self.config['fps']}")
        
        return {
            "status": "configured",
            "mode": self.mode,
            "resolution": res,
            "samples": self.config['samples'],
            "fps": self.config['fps'],
            "denoiser": self.config['denoiser']
        }
    
    def render_frame_range(
        self, 
        output_dir: str, 
        start_frame: int, 
        end_frame: int,
        frame_prefix: str = "frame_"
    ) -> List[str]:
        """
        Rend une plage de frames.
        
        Args:
            output_dir: Dossier de sortie
            start_frame: Frame de début
            end_frame: Frame de fin
            frame_prefix: Préfixe des fichiers
            
        Returns:
            Liste des chemins des frames rendues
        """
        if not BPY_AVAILABLE:
            self._log(f"⚠️ bpy non disponible - rendu simulé ({start_frame}-{end_frame})")
            return [f"{output_dir}/{frame_prefix}{f:04d}.png" for f in range(start_frame, end_frame + 1)]
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        scene = bpy.context.scene
        rendered_frames = []
        
        total_frames = end_frame - start_frame + 1
        render_start = time.time()
        
        self._log(f"Début rendu: frames {start_frame}-{end_frame} ({total_frames} frames)")
        
        for frame in range(start_frame, end_frame + 1):
            frame_start = time.time()
            
            scene.frame_set(frame)
            frame_path = f"{output_dir}/{frame_prefix}{frame:04d}.png"
            scene.render.filepath = frame_path
            
            bpy.ops.render.render(write_still=True)
            
            rendered_frames.append(frame_path)
            
            frame_time = time.time() - frame_start
            progress = (frame - start_frame + 1) / total_frames * 100
            self._log(f"  ⚗️ Frame {frame}/{end_frame} ({progress:.1f}%) - {frame_time:.1f}s")
        
        total_time = time.time() - render_start
        avg_time = total_time / total_frames
        
        self._log(f"✓ Rendu terminé: {total_frames} frames en {total_time:.1f}s ({avg_time:.2f}s/frame)")
        
        return rendered_frames
    
    def render_animation(
        self, 
        output_dir: str,
        frame_prefix: str = "frame_"
    ) -> Dict[str, Any]:
        """
        Rend l'animation complète de la scène.
        
        Args:
            output_dir: Dossier de sortie
            frame_prefix: Préfixe des fichiers
            
        Returns:
            Dict avec les métadonnées du rendu
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - rendu animation simulé")
            return {
                "status": "simulated",
                "frames_dir": output_dir,
                "frame_count": 100,
                "resolution": self.config['render_resolution'],
                "fps": self.config['fps']
            }
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        scene = bpy.context.scene
        scene.render.filepath = f"{output_dir}/{frame_prefix}"
        
        start_frame = scene.frame_start
        end_frame = scene.frame_end
        total_frames = end_frame - start_frame + 1
        
        self._log(f"Rendu animation: frames {start_frame}-{end_frame}")
        
        render_start = time.time()
        bpy.ops.render.render(animation=True)
        total_time = time.time() - render_start
        
        self._log(f"✓ Animation rendue: {total_frames} frames en {total_time:.1f}s")
        
        return {
            "status": "success",
            "frames_dir": output_dir,
            "frame_count": total_frames,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "resolution": self.config['render_resolution'],
            "fps": self.config['fps'],
            "render_time_seconds": total_time
        }
    
    def render_single_frame(
        self, 
        output_path: str,
        frame: Optional[int] = None
    ) -> str:
        """
        Rend une seule frame.
        
        Args:
            output_path: Chemin de sortie complet
            frame: Numéro de frame (None = frame courante)
            
        Returns:
            Chemin de la frame rendue
        """
        if not BPY_AVAILABLE:
            self._log(f"⚠️ bpy non disponible - rendu simulé: {output_path}")
            return output_path
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        scene = bpy.context.scene
        
        if frame is not None:
            scene.frame_set(frame)
        
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        
        self._log(f"✓ Frame rendue: {output_path}")
        
        return output_path
    
    def get_scene_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de la scène courante.
        
        Returns:
            Dict avec les infos de scène
        """
        if not BPY_AVAILABLE:
            return {
                "status": "no_bpy",
                "frame_start": 1,
                "frame_end": 100,
                "fps": self.config['fps']
            }
        
        scene = bpy.context.scene
        
        return {
            "status": "ok",
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "frame_current": scene.frame_current,
            "fps": scene.render.fps / scene.render.fps_base,
            "resolution": (scene.render.resolution_x, scene.render.resolution_y),
            "samples": scene.cycles.samples if scene.render.engine == 'CYCLES' else None,
            "engine": scene.render.engine
        }


if __name__ == "__main__":
    print("=" * 60)
    print("⚗️ CYCLES RENDERER - Test Mode")
    print("=" * 60)
    
    print(f"\n📋 TURBO_MODES disponibles:")
    for mode, config in TURBO_MODES.items():
        res = config['render_resolution']
        final_res = config['final_resolution']
        print(f"   {mode.upper()}: {res[0]}x{res[1]} → {final_res[0]}x{final_res[1]}")
        print(f"      Samples: {config['samples']}, FPS: {config['fps']} → {config['final_fps']}")
    
    print(f"\n🔧 BPY_AVAILABLE: {BPY_AVAILABLE}")
    
    for mode in TURBO_MODES.keys():
        print(f"\n🧪 Test mode {mode.upper()}:")
        renderer = CyclesRenderer(turbo_mode=mode, verbose=True)
        config = renderer.configure_cycles()
        print(f"   Config: {config}")
    
    print("\n✅ Module cycles_renderer.py fonctionnel")
