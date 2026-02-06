#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Frégate DIRECTEUR PHOTO - Format Adapter
Conversion multi-format: 16:9 → 9:16 / 1:1 pour TikTok, Reels, YouTube.

Adapte automatiquement la résolution et compense le FOV pour éviter
les bandes noires lors du passage de l'horizontal au vertical.
"""

from typing import Any, Dict, Optional, Tuple

try:
    import bpy
    BPY_AVAILABLE = True
except ImportError:
    BPY_AVAILABLE = False
    bpy = None


OUTPUT_FORMATS = {
    "HORIZONTAL": {
        "width": 1920,
        "height": 1080,
        "ratio": 16/9,
        "name": "YouTube / Standard",
        "platforms": ["YouTube", "Desktop"]
    },
    "VERTICAL": {
        "width": 1080,
        "height": 1920,
        "ratio": 9/16,
        "name": "TikTok / Reels",
        "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"]
    },
    "SQUARE": {
        "width": 1080,
        "height": 1080,
        "ratio": 1/1,
        "name": "Instagram Feed",
        "platforms": ["Instagram Feed", "Facebook"]
    },
    "CINEMATIC": {
        "width": 1920,
        "height": 800,
        "ratio": 2.4/1,
        "name": "Cinématique 2.4:1",
        "platforms": ["Cinéma", "Premium"]
    },
    "IPHONE_MAX": {
        "width": 1290,
        "height": 2796,
        "ratio": 1290/2796,
        "name": "iPhone 15 Pro Max",
        "platforms": ["iPhone"]
    }
}

MAX_ZOOM_FACTOR = 1.3


class FormatAdapter:
    """
    Adapte le rendu pour différents formats de sortie.
    
    Fonctionnalités:
    - Configuration résolution de rendu
    - Compensation FOV pour éviter bandes noires
    - Préservation de la zone d'intérêt lors du crop
    
    Usage:
        adapter = FormatAdapter()
        adapter.configure_render_resolution("VERTICAL")
        adapter.compensate_fov(camera, source_ratio=16/9, target_ratio=9/16)
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Affiche les logs
        """
        self.verbose = verbose
        self.original_settings: Dict = {}
    
    def _log(self, message: str) -> None:
        """Log conditionnel."""
        if self.verbose:
            print(f"📐 [FormatAdapter] {message}")
    
    def get_available_formats(self) -> Dict:
        """
        Retourne tous les formats disponibles.
        
        Returns:
            Dict des formats avec leurs caractéristiques
        """
        return OUTPUT_FORMATS.copy()
    
    def configure_render_resolution(
        self,
        target_format: str = "VERTICAL",
        custom_width: Optional[int] = None,
        custom_height: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Configure la résolution de rendu.
        
        Args:
            target_format: Nom du format (HORIZONTAL, VERTICAL, SQUARE, etc.)
            custom_width: Largeur personnalisée (override)
            custom_height: Hauteur personnalisée (override)
            
        Returns:
            (width, height) configurés
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - configuration impossible")
            if target_format in OUTPUT_FORMATS:
                fmt = OUTPUT_FORMATS[target_format]
                return (fmt["width"], fmt["height"])
            return (1080, 1920)
        
        scene = bpy.context.scene
        
        self.original_settings = {
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "resolution_percentage": scene.render.resolution_percentage
        }
        
        if custom_width and custom_height:
            width, height = custom_width, custom_height
            format_name = f"Custom ({width}x{height})"
        elif target_format in OUTPUT_FORMATS:
            fmt = OUTPUT_FORMATS[target_format]
            width, height = fmt["width"], fmt["height"]
            format_name = fmt["name"]
        else:
            self._log(f"⚠️ Format '{target_format}' inconnu - défaut VERTICAL")
            fmt = OUTPUT_FORMATS["VERTICAL"]
            width, height = fmt["width"], fmt["height"]
            format_name = fmt["name"]
        
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        
        ratio = width / height
        self._log(f"✓ Résolution configurée: {format_name}")
        self._log(f"  {width}x{height} (ratio {ratio:.2f})")
        
        return (width, height)
    
    def restore_original_resolution(self) -> bool:
        """
        Restaure les paramètres de résolution originaux.
        
        Returns:
            True si restauration réussie
        """
        if not BPY_AVAILABLE or not self.original_settings:
            return False
        
        scene = bpy.context.scene
        scene.render.resolution_x = self.original_settings["resolution_x"]
        scene.render.resolution_y = self.original_settings["resolution_y"]
        scene.render.resolution_percentage = self.original_settings["resolution_percentage"]
        
        self._log("✓ Résolution originale restaurée")
        return True
    
    def compensate_fov(
        self,
        camera: Any,
        source_ratio: float = 16/9,
        target_ratio: float = 9/16,
        max_zoom: Optional[float] = None
    ) -> float:
        """
        Compense le FOV lors du passage horizontal → vertical.
        
        Lors du crop vertical, on perd les côtés de l'image.
        Cette méthode zoome légèrement pour remplir le cadre
        sans laisser de bandes noires.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            source_ratio: Ratio de capture original (défaut: 16/9)
            target_ratio: Ratio de sortie (défaut: 9/16)
            max_zoom: Facteur de zoom maximum (défaut: MAX_ZOOM_FACTOR)
            
        Returns:
            Facteur de compensation appliqué
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible - compensation impossible")
            return 1.0
        
        max_z = max_zoom if max_zoom is not None else MAX_ZOOM_FACTOR
        
        if target_ratio >= source_ratio:
            self._log("  Pas de compensation nécessaire (target >= source)")
            return 1.0
        
        crop_factor = target_ratio / source_ratio
        
        zoom_compensation = min(1 / crop_factor, max_z)
        
        original_lens = camera.data.lens
        new_lens = original_lens / zoom_compensation
        camera.data.lens = new_lens
        
        self._log(f"✓ FOV compensé sur {camera.name}")
        self._log(f"  Ratio source: {source_ratio:.2f} → target: {target_ratio:.2f}")
        self._log(f"  Crop factor: {crop_factor:.3f}")
        self._log(f"  Zoom compensation: {zoom_compensation:.3f}x")
        self._log(f"  Focale: {original_lens:.1f}mm → {new_lens:.1f}mm")
        
        return zoom_compensation
    
    def calculate_safe_area(
        self,
        source_ratio: float = 16/9,
        target_ratio: float = 9/16
    ) -> Dict[str, float]:
        """
        Calcule la zone de sécurité pour les éléments importants.
        
        La zone de sécurité est la région visible dans tous les formats.
        Utile pour positionner les sujets principaux.
        
        Args:
            source_ratio: Ratio de capture
            target_ratio: Ratio de sortie
            
        Returns:
            Dict avec left, right, top, bottom en proportions [0, 1]
        """
        if source_ratio == target_ratio:
            return {"left": 0, "right": 1, "top": 0, "bottom": 1}
        
        if source_ratio > target_ratio:
            safe_width = target_ratio / source_ratio
            margin = (1 - safe_width) / 2
            return {
                "left": margin,
                "right": 1 - margin,
                "top": 0,
                "bottom": 1
            }
        else:
            safe_height = source_ratio / target_ratio
            margin = (1 - safe_height) / 2
            return {
                "left": 0,
                "right": 1,
                "top": margin,
                "bottom": 1 - margin
            }
    
    def setup_composition_guides(
        self,
        camera: Any,
        show_safe_area: bool = True,
        show_thirds: bool = True
    ) -> None:
        """
        Configure les guides de composition dans le viewport.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            show_safe_area: Affiche la zone de sécurité
            show_thirds: Affiche la règle des tiers
        """
        if not BPY_AVAILABLE:
            self._log("⚠️ bpy non disponible")
            return
        
        camera.data.show_composition_thirds = show_thirds
        camera.data.show_composition_center = True
        camera.data.show_safe_areas = show_safe_area
        
        if show_safe_area:
            camera.data.safe_areas.title = (0.9, 0.9)
            camera.data.safe_areas.action = (0.8, 0.8)
        
        self._log(f"✓ Guides de composition configurés sur {camera.name}")
    
    def get_render_info(self) -> Dict:
        """
        Retourne les informations de rendu actuelles.
        
        Returns:
            Dict avec résolution et paramètres
        """
        if not BPY_AVAILABLE:
            return {"error": "bpy non disponible"}
        
        scene = bpy.context.scene
        width = scene.render.resolution_x
        height = scene.render.resolution_y
        
        format_match = None
        for name, fmt in OUTPUT_FORMATS.items():
            if fmt["width"] == width and fmt["height"] == height:
                format_match = name
                break
        
        return {
            "resolution_x": width,
            "resolution_y": height,
            "ratio": width / height if height > 0 else 0,
            "percentage": scene.render.resolution_percentage,
            "format": format_match,
            "fps": scene.render.fps,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end
        }
    
    def setup_for_platform(
        self,
        camera: Any,
        platform: str = "TikTok"
    ) -> Tuple[int, int]:
        """
        Configuration rapide pour une plateforme spécifique.
        
        Args:
            camera: bpy.types.Object de type CAMERA
            platform: Nom de la plateforme
            
        Returns:
            (width, height) configurés
        """
        platform_lower = platform.lower()
        
        platform_map = {
            "tiktok": "VERTICAL",
            "reels": "VERTICAL",
            "shorts": "VERTICAL",
            "instagram": "SQUARE",
            "youtube": "HORIZONTAL",
            "cinematic": "CINEMATIC"
        }
        
        target_format = platform_map.get(platform_lower, "VERTICAL")
        
        self._log(f"Configuration pour {platform} → format {target_format}")
        
        width, height = self.configure_render_resolution(target_format)
        
        source_ratio = 16/9
        target_ratio = width / height
        self.compensate_fov(camera, source_ratio, target_ratio)
        
        return (width, height)


if __name__ == "__main__":
    print("=" * 50)
    print("📐 FORMAT ADAPTER - Test Mode")
    print("=" * 50)
    
    print(f"\n📋 Formats disponibles:")
    for name, fmt in OUTPUT_FORMATS.items():
        print(f"   {name}: {fmt['width']}x{fmt['height']} ({fmt['name']})")
        print(f"      Ratio: {fmt['ratio']:.3f}, Platforms: {fmt['platforms']}")
    
    print(f"\n📋 Configuration:")
    print(f"   MAX_ZOOM_FACTOR: {MAX_ZOOM_FACTOR}")
    print(f"   BPY_AVAILABLE: {BPY_AVAILABLE}")
    
    adapter = FormatAdapter(verbose=True)
    print(f"\n✅ FormatAdapter initialisé")
    
    print("\n🧪 Test calcul zone de sécurité:")
    safe = adapter.calculate_safe_area(16/9, 9/16)
    print(f"   16:9 → 9:16")
    print(f"   Zone safe: left={safe['left']:.3f}, right={safe['right']:.3f}")
    print(f"   (centre horizontal conservé)")
    
    safe2 = adapter.calculate_safe_area(9/16, 16/9)
    print(f"\n   9:16 → 16:9")
    print(f"   Zone safe: top={safe2['top']:.3f}, bottom={safe2['bottom']:.3f}")
    
    if BPY_AVAILABLE:
        print("\n🎬 Test avec scène Blender:")
        adapter.configure_render_resolution("VERTICAL")
        info = adapter.get_render_info()
        print(f"   Render info: {info}")
        
        if bpy.context.scene.camera:
            cam = bpy.context.scene.camera
            adapter.setup_for_platform(cam, "TikTok")
    
    print("\n✅ Module format_adapter.py fonctionnel")
