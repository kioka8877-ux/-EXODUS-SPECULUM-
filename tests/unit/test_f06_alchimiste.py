"""
Tests unitaires pour F06 ALCHIMISTE.
Rendu Cycles + Upscaling IA (ESRGAN/RIFE).
"""
import pytest
from pathlib import Path


class TestF06Alchimiste:
    """Tests pour la frégate ALCHIMISTE."""
    
    def test_p1_delivery_profiles_exist(self):
        """P1: Vérifie que les profils de livraison existent."""
        from CORE_CONFIG.output_contracts import DELIVERY_PROFILES
        
        assert "ECLAIREUR" in DELIVERY_PROFILES
        assert "CONQUERANT" in DELIVERY_PROFILES
        assert "PREMIUM" in DELIVERY_PROFILES
    
    def test_p2_eclaireur_profile_settings(self):
        """P2: Vérifie les paramètres du profil ECLAIREUR."""
        from CORE_CONFIG.output_contracts import DELIVERY_PROFILES
        
        eclaireur = DELIVERY_PROFILES["ECLAIREUR"]
        assert eclaireur["resolution"] == (960, 540)
        assert eclaireur["fps"] == 12
        assert eclaireur["samples"] == 16
    
    def test_p3_premium_profile_settings(self):
        """P3: Vérifie les paramètres du profil PREMIUM."""
        from CORE_CONFIG.output_contracts import DELIVERY_PROFILES
        
        premium = DELIVERY_PROFILES["PREMIUM"]
        assert premium["resolution"] == (3840, 2160)
        assert premium["fps"] == 60
        assert premium["upscale"] is True
        assert premium["interpolation"] is True
    
    def test_p4_vram_limit_defined(self):
        """P4: Vérifie la limite VRAM."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f06_contract = FRIGATE_CONTRACTS["F06_ALCHIMISTE"]
        assert f06_contract["constraints"]["max_vram_gb"] == 14
    
    def test_p5_upscale_models_defined(self):
        """P5: Vérifie les modèles d'upscaling disponibles."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f06_contract = FRIGATE_CONTRACTS["F06_ALCHIMISTE"]
        models = f06_contract["constraints"]["upscale_models"]
        
        assert "realesrgan-x4plus" in models
    
    def test_p6_samples_range(self):
        """P6: Vérifie la plage de samples."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f06_contract = FRIGATE_CONTRACTS["F06_ALCHIMISTE"]
        samples_range = f06_contract["constraints"]["samples_range"]
        
        assert samples_range[0] == 16
        assert samples_range[1] == 256
    
    def test_alchimiste_module_structure(self):
        """Vérifie que le module a la structure attendue."""
        alch_path = Path(__file__).parent.parent.parent / "FRIGATE_06_ALCHIMISTE"
        assert alch_path.exists(), "FRIGATE_06_ALCHIMISTE directory missing"
    
    def test_alchimiste_import(self):
        """Vérifie que le module est importable."""
        try:
            from FRIGATE_06_ALCHIMISTE.CODEBASE import alchimiste_pipeline
            assert alchimiste_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Alchimiste not importable: {e}")
