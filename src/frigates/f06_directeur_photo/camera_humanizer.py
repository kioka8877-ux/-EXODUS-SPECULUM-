#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO - Camera Humanizer
Configure la caméra comme un iPhone tenu à la main avec effets de marche et respiration.

L'Œil de l'Envie: Recréer le style "Femme qui filme avec son iPhone"
pour maximiser l'authenticité et la viralité sur TikTok/Reels.
"""

import math
from typing import Any, Optional

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


IPHONE_FOCAL_LENGTH = 26
HANDHELD_Z_FREQ = 1.8
HANDHELD_Z_AMPLITUDE = 0.02
HANDHELD_ROT_NOISE = 0.005
HANDHELD_BREATHING_CYCLE = 4.0


class CameraHumanizer:
    """
    Configure la caméra pour simuler un iPhone tenu à la main.
    
    Effets appliqués:
    - Focale iPhone (26mm équivalent)
    - Walking bounce (oscillation Z pendant la marche)
    - Breathing zoom (variation focale sur cycle de respiration)
    
    Usage:
        humanizer = CameraHumanizer()
        humanizer.setup_iphone_camera(camera)
        humanizer.add_walking_bounce(camera, duration_frames=720)
        humanizer.add_breathing_zoom(camera, fps=24)
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs de configuration
        """
        self.verbose = verbose
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"📷 [CameraHumanizer] {message}")
    
    def setup_iphone_camera(self, camera: Any) -> None:
        """
        Configure la caméra comme un iPhone.
        
        Args:
            camera: bpy.types.Object de type CAMERA
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - setup impossible")
            return
        
        if camera.type != 'CAMERA':
            raise ValueError(f"L'objet {camera.name} n'est pas une caméra")
        
        camera.data.lens = IPHONE_FOCAL_LENGTH
        camera.data.sensor_width = 36
        camera.data.sensor_fit = 'HORIZONTAL'
        
        self._log(f"✓ Caméra {camera.name} configurée en mode iPhone")
        self._log(f"  Focale: {IPHONE_FOCAL_LENGTH}mm, Sensor: 36mm")
    
    def add_walking_bounce(
        self, 
        camera: Any, 
        duration_frames: int,
        fps: int = 24,
        amplitude: Optional[float] = None,
        frequency: Optional[float] = None
    ) -> None:
        """
        Oscillation sinusoïdale sur Z pour simuler le pas pendant la marche.
        
        z(t) = base_z + AMPLITUDE * sin(2π * FREQ * t)
        
        Args:
            camera: bpy.types.Object de type CAMERA
            duration_frames: Nombre total de frames
            fps: Frames par seconde (défaut: 24)
            amplitude: Override amplitude (défaut: HANDHELD_Z_AMPLITUDE)
            frequency: Override fréquence (défaut: HANDHELD_Z_FREQ)
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - bounce impossible")
            return
        
        amp = amplitude if amplitude is not None else HANDHELD_Z_AMPLITUDE
        freq = frequency if frequency is not None else HANDHELD_Z_FREQ
        base_z = camera.location.z
        
        if not camera.animation_data:
            camera.animation_data_create()
        if not camera.animation_data.action:
            camera.animation_data.action = bpy.data.actions.new(name=f"Handheld_Motion_{camera.name}")
        
        z_fcurve = None
        for fc in camera.animation_data.action.fcurves:
            if fc.data_path == 'location' and fc.array_index == 2:
                z_fcurve = fc
                break
        
        if z_fcurve is None:
            z_fcurve = camera.animation_data.action.fcurves.new(data_path='location', index=2)
        else:
            z_fcurve.keyframe_points.clear()
        
        for frame in range(duration_frames):
            t = frame / fps
            z_offset = amp * math.sin(2 * math.pi * freq * t)
            z_fcurve.keyframe_points.insert(frame, base_z + z_offset)
        
        for kp in z_fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        
        self._log(f"✓ Walking bounce appliqué sur {camera.name}")
        self._log(f"  Durée: {duration_frames} frames ({duration_frames/fps:.1f}s)")
        self._log(f"  Amplitude: {amp}m, Fréquence: {freq}Hz")
    
    def add_breathing_zoom(
        self,
        camera: Any,
        fps: int = 24,
        variation_mm: float = 2.0,
        cycle_duration: Optional[float] = None
    ) -> None:
        """
        Cycle de respiration subtil via driver sur focal length.
        
        lens(t) = base_lens + variation * sin(2π * t / cycle)
        
        Args:
            camera: bpy.types.Object de type CAMERA
            fps: Frames par seconde
            variation_mm: Variation de focale en mm (±)
            cycle_duration: Durée d'un cycle en secondes (défaut: HANDHELD_BREATHING_CYCLE)
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - breathing zoom impossible")
            return
        
        cycle = cycle_duration if cycle_duration is not None else HANDHELD_BREATHING_CYCLE
        base_lens = camera.data.lens
        
        if camera.data.animation_data:
            for driver in camera.data.animation_data.drivers:
                if driver.data_path == 'lens':
                    camera.data.animation_data.drivers.remove(driver)
                    break
        
        driver = camera.data.driver_add('lens').driver
        driver.type = 'SCRIPTED'
        driver.expression = f"{base_lens} + {variation_mm} * sin(frame / {fps} * 2 * 3.14159 / {cycle})"
        
        self._log(f"✓ Breathing zoom configuré sur {camera.name}")
        self._log(f"  Focale base: {base_lens}mm ± {variation_mm}mm")
        self._log(f"  Cycle: {cycle}s")
    
    def get_camera_info(self, camera: Any) -> dict:
        """
        Retourne les informations de configuration de la caméra.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            
        Returns:
            Dict avec les paramètres actuels
        """
        if not BPY_AVAILABLE:
            return {"error": "bpy non disponible"}
        
        info = {
            "name": camera.name,
            "focal_length": camera.data.lens,
            "sensor_width": camera.data.sensor_width,
            "sensor_fit": camera.data.sensor_fit,
            "location": tuple(camera.location),
            "rotation": tuple(camera.rotation_euler),
            "has_animation": camera.animation_data is not None,
            "has_driver": False
        }
        
        if camera.data.animation_data:
            for driver in camera.data.animation_data.drivers:
                if driver.data_path == 'lens':
                    info["has_driver"] = True
                    info["driver_expression"] = driver.driver.expression
                    break
        
        return info


if __name__ == "__main__":
    print("=" * 50)
    print("📷 CAMERA HUMANIZER - Test Mode")
    print("=" * 50)
    
    print(f"\n📋 Constantes iPhone:")
    print(f"   IPHONE_FOCAL_LENGTH: {IPHONE_FOCAL_LENGTH}mm")
    print(f"   HANDHELD_Z_FREQ: {HANDHELD_Z_FREQ}Hz")
    print(f"   HANDHELD_Z_AMPLITUDE: {HANDHELD_Z_AMPLITUDE}m")
    print(f"   HANDHELD_ROT_NOISE: {HANDHELD_ROT_NOISE}rad")
    print(f"   HANDHELD_BREATHING_CYCLE: {HANDHELD_BREATHING_CYCLE}s")
    
    humanizer = CameraHumanizer(verbose=True)
    print(f"\n✅ CameraHumanizer initialisé (bpy_available={BPY_AVAILABLE})")
    
    if BPY_AVAILABLE:
        print("\n🎬 Test avec scène Blender active:")
        if bpy.context.scene.camera:
            cam = bpy.context.scene.camera
            humanizer.setup_iphone_camera(cam)
            humanizer.add_walking_bounce(cam, duration_frames=720, fps=24)
            humanizer.add_breathing_zoom(cam, fps=24)
            info = humanizer.get_camera_info(cam)
            print(f"   Camera info: {info}")
    
    print("\n✅ Module camera_humanizer.py fonctionnel")
