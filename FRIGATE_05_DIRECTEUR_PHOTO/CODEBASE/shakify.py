#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO - Shakify
Bruit de Perlin pour micro-tremblements naturels du poignet.

Plus organique que random.gauss() - évite les mouvements saccadés
pour simuler le tremblement naturel d'une personne tenant un iPhone.
"""

import math
import random
from typing import Any, Optional, List, Tuple

try:
    import bpy
    from mathutils import noise as blender_noise
    BPY_AVAILABLE = True
    MATHUTILS_NOISE = True
except ImportError:
    BPY_AVAILABLE = False
    MATHUTILS_NOISE = False
    bpy = None
    blender_noise = None


HANDHELD_ROT_NOISE = 0.005


class Shakify:
    """
    Génère du bruit de Perlin pour simuler les micro-tremblements du poignet.
    
    Utilise mathutils.noise si disponible (Blender), sinon implémentation pure Python.
    
    Axes affectés:
    - Axe X (Pitch): Hochement de tête
    - Axe Y (Roll): Inclinaison latérale
    - Axe Z: Ignoré (rotation horizontale = intentionnelle par l'utilisateur)
    
    Usage:
        shakify = Shakify(seed=42)
        shakify.apply_rotation_shake(camera, duration_frames=720)
    """
    
    def __init__(self, seed: int = 42, verbose: bool = True):
        """
        Args:
            seed: Graine pour le bruit pseudo-aléatoire
            verbose: Affiche les logs
        """
        self.seed = seed
        self.verbose = verbose
        self._permutation = self._generate_permutation()
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"🎲 [Shakify] {message}")
    
    def _generate_permutation(self) -> List[int]:
        """Génère la table de permutation pour le bruit de Perlin."""
        random.seed(self.seed)
        perm = list(range(256))
        random.shuffle(perm)
        return perm + perm
    
    def _fade(self, t: float) -> float:
        """Fonction de lissage 6t^5 - 15t^4 + 10t^3."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Interpolation linéaire."""
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float) -> float:
        """Gradient 1D."""
        h = hash_val & 1
        return x if h == 0 else -x
    
    def perlin_noise_1d(
        self, 
        x: float, 
        octaves: int = 4, 
        persistence: float = 0.5
    ) -> float:
        """
        Génère du bruit de Perlin 1D avec plusieurs octaves.
        
        Args:
            x: Position sur l'axe
            octaves: Nombre de couches de détail
            persistence: Atténuation par octave (0.5 = moitié)
            
        Returns:
            Valeur de bruit normalisée [-1, 1]
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            xi = int(x * frequency) & 255
            xf = (x * frequency) - int(x * frequency)
            
            u = self._fade(xf)
            
            a = self._permutation[xi]
            b = self._permutation[xi + 1]
            
            n = self._lerp(
                self._grad(a, xf),
                self._grad(b, xf - 1),
                u
            )
            
            total += n * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        return total / max_value if max_value > 0 else 0.0
    
    def perlin_noise_3d(
        self,
        x: float,
        y: float,
        z: float
    ) -> float:
        """
        Utilise mathutils.noise si disponible, sinon fallback.
        
        Args:
            x, y, z: Coordonnées 3D
            
        Returns:
            Valeur de bruit [-1, 1]
        """
        if MATHUTILS_NOISE:
            return blender_noise.noise((x, y, z))
        
        return self.perlin_noise_1d(x + y * 10 + z * 100)
    
    def apply_rotation_shake(
        self,
        camera: Any,
        duration_frames: int,
        intensity: Optional[float] = None,
        fps: int = 24,
        axes: Tuple[int, ...] = (0, 1)
    ) -> None:
        """
        Applique le bruit de Perlin sur les rotations pour simuler le tremblement.
        
        Args:
            camera: bpy.types.Object
            duration_frames: Nombre total de frames
            intensity: Force du tremblement en radians (défaut: HANDHELD_ROT_NOISE)
            fps: Frames par seconde
            axes: Indices des axes à affecter (défaut: X=0, Y=1)
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - shake impossible")
            return
        
        noise_intensity = intensity if intensity is not None else HANDHELD_ROT_NOISE
        
        if not camera.animation_data:
            camera.animation_data_create()
        if not camera.animation_data.action:
            camera.animation_data.action = bpy.data.actions.new(name=f"Handheld_Shake_{camera.name}")
        
        axis_names = ['X (Pitch)', 'Y (Roll)', 'Z (Yaw)']
        
        for axis_index in axes:
            fcurve = None
            for fc in camera.animation_data.action.fcurves:
                if fc.data_path == 'rotation_euler' and fc.array_index == axis_index:
                    fcurve = fc
                    break
            
            if fcurve is None:
                fcurve = camera.animation_data.action.fcurves.new(
                    data_path='rotation_euler',
                    index=axis_index
                )
            else:
                fcurve.keyframe_points.clear()
            
            base_rot = camera.rotation_euler[axis_index]
            
            for frame in range(duration_frames):
                t = frame / fps
                
                if MATHUTILS_NOISE:
                    noise_val = blender_noise.noise((
                        t * 2,
                        axis_index * 10 + self.seed,
                        self.seed * 0.1
                    )) * noise_intensity
                else:
                    noise_val = self.perlin_noise_1d(
                        t * 2 + axis_index * 100
                    ) * noise_intensity
                
                fcurve.keyframe_points.insert(frame, base_rot + noise_val)
            
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
            
            self._log(f"  ✓ Shake appliqué sur {axis_names[axis_index]}")
        
        self._log(f"✓ Rotation shake appliqué sur {camera.name}")
        self._log(f"  Durée: {duration_frames} frames ({duration_frames/fps:.1f}s)")
        self._log(f"  Intensité: {noise_intensity} rad ({math.degrees(noise_intensity):.2f}°)")
    
    def apply_location_shake(
        self,
        camera: Any,
        duration_frames: int,
        intensity: float = 0.005,
        fps: int = 24,
        axes: Tuple[int, ...] = (0, 1)
    ) -> None:
        """
        Applique un léger tremblement sur la position (X, Y).
        
        Complémentaire au rotation shake pour plus de réalisme.
        
        Args:
            camera: bpy.types.Object
            duration_frames: Nombre total de frames
            intensity: Amplitude du tremblement en mètres
            fps: Frames par seconde
            axes: Indices des axes à affecter (défaut: X=0, Y=1)
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - location shake impossible")
            return
        
        if not camera.animation_data:
            camera.animation_data_create()
        if not camera.animation_data.action:
            camera.animation_data.action = bpy.data.actions.new(name=f"Handheld_Shake_{camera.name}")
        
        axis_names = ['X', 'Y', 'Z']
        
        for axis_index in axes:
            fcurve = None
            for fc in camera.animation_data.action.fcurves:
                if fc.data_path == 'location' and fc.array_index == axis_index:
                    fcurve = fc
                    break
            
            if fcurve is None:
                fcurve = camera.animation_data.action.fcurves.new(
                    data_path='location',
                    index=axis_index
                )
            
            base_loc = camera.location[axis_index]
            existing_values = {int(kp.co[0]): kp.co[1] for kp in fcurve.keyframe_points}
            
            for frame in range(duration_frames):
                t = frame / fps
                
                if MATHUTILS_NOISE:
                    noise_val = blender_noise.noise((
                        t * 3,
                        axis_index * 20 + self.seed + 50,
                        self.seed * 0.2
                    )) * intensity
                else:
                    noise_val = self.perlin_noise_1d(
                        t * 3 + axis_index * 200 + 50
                    ) * intensity
                
                if frame in existing_values:
                    new_val = existing_values[frame] + noise_val
                else:
                    new_val = base_loc + noise_val
                
                fcurve.keyframe_points.insert(frame, new_val)
            
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
            
            self._log(f"  ✓ Location shake sur axe {axis_names[axis_index]}")
        
        self._log(f"✓ Location shake appliqué sur {camera.name}")
    
    def generate_shake_curve(
        self,
        duration_frames: int,
        fps: int = 24,
        intensity: float = 1.0
    ) -> List[float]:
        """
        Génère une courbe de shake sans l'appliquer.
        
        Utile pour prévisualisation ou export.
        
        Args:
            duration_frames: Nombre de frames
            fps: Frames par seconde
            intensity: Multiplicateur d'intensité
            
        Returns:
            Liste des valeurs de bruit
        """
        values = []
        for frame in range(duration_frames):
            t = frame / fps
            if MATHUTILS_NOISE:
                val = blender_noise.noise((t * 2, self.seed, 0)) * intensity
            else:
                val = self.perlin_noise_1d(t * 2) * intensity
            values.append(val)
        return values


if __name__ == "__main__":
    print("=" * 50)
    print("🎲 SHAKIFY - Test Mode")
    print("=" * 50)
    
    print(f"\n📋 Configuration:")
    print(f"   HANDHELD_ROT_NOISE: {HANDHELD_ROT_NOISE} rad ({math.degrees(HANDHELD_ROT_NOISE):.2f}°)")
    print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
    print(f"   MATHUTILS_NOISE: {MATHUTILS_NOISE}")
    
    shakify = Shakify(seed=42, verbose=True)
    print(f"\n✅ Shakify initialisé avec seed=42")
    
    print("\n🧪 Test bruit de Perlin 1D:")
    for i in range(5):
        t = i * 0.25
        noise_val = shakify.perlin_noise_1d(t)
        print(f"   t={t:.2f}: {noise_val:.4f}")
    
    print("\n📊 Test courbe de shake (10 frames):")
    curve = shakify.generate_shake_curve(10, fps=24, intensity=HANDHELD_ROT_NOISE)
    for i, val in enumerate(curve):
        bar = "█" * int(abs(val) * 500 + 1)
        sign = "+" if val >= 0 else "-"
        print(f"   Frame {i:2d}: {sign}{bar} ({val:.5f})")
    
    if BPY_AVAILABLE and bpy.context.scene.camera:
        print("\n🎬 Test avec scène Blender:")
        cam = bpy.context.scene.camera
        shakify.apply_rotation_shake(cam, duration_frames=100, fps=24)
    
    print("\n✅ Module shakify.py fonctionnel")
