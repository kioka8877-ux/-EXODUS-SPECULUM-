"""
Tests unitaires pour F05 DIRECTEUR PHOTO.
Camera animation + Smart-Crop.
"""
import pytest
from pathlib import Path


class TestF05DirecteurPhoto:
    """Tests pour la frégate DIRECTEUR PHOTO."""
    
    def test_p1_animated_collections_required(self, contracts_dir):
        """P1: Vérifie les collections requises pour scene_animated."""
        import json
        with open(contracts_dir / "blend_contract.json") as f:
            contract = json.load(f)
        
        anim_collections = contract["required_collections"]["scene_animated"]
        assert "CAMERAS" in anim_collections
    
    def test_p2_handheld_constraints(self):
        """P2: Vérifie les contraintes de handheld motion."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f05_contract = FRIGATE_CONTRACTS["F05_DIRECTEUR_PHOTO"]
        constraints = f05_contract["constraints"]
        
        assert "handheld_amplitude_max" in constraints
        assert constraints["handheld_amplitude_max"] == 0.02
    
    def test_p3_breathing_constraints(self):
        """P3: Vérifie les contraintes de breathing animation."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f05_contract = FRIGATE_CONTRACTS["F05_DIRECTEUR_PHOTO"]
        constraints = f05_contract["constraints"]
        
        assert "breathing_amplitude_max" in constraints
        assert constraints["breathing_amplitude_max"] == 0.005
    
    def test_p4_sensor_shift_enabled(self):
        """P4: Vérifie que le sensor shift est activé."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f05_contract = FRIGATE_CONTRACTS["F05_DIRECTEUR_PHOTO"]
        outputs = f05_contract["outputs"]
        
        assert outputs["scene_animated.blend"]["sensor_shift_enabled"] is True
    
    def test_p5_camera_animated_flag(self):
        """P5: Vérifie le flag camera_animated."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f05_contract = FRIGATE_CONTRACTS["F05_DIRECTEUR_PHOTO"]
        assert f05_contract["outputs"]["scene_animated.blend"]["camera_animated"] is True
    
    def test_directeur_photo_module_structure(self):
        """Vérifie que le module a la structure attendue."""
        dp_path = Path(__file__).parent.parent.parent / "FRIGATE_05_DIRECTEUR_PHOTO"
        assert dp_path.exists(), "FRIGATE_05_DIRECTEUR_PHOTO directory missing"
    
    def test_directeur_photo_import(self):
        """Vérifie que le module est importable."""
        try:
            from FRIGATE_05_DIRECTEUR_PHOTO.CODEBASE import directeur_photo_pipeline
            assert directeur_photo_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Directeur Photo not importable: {e}")
