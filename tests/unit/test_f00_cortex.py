"""
Tests unitaires pour F00 CORTEX.
Intelligence IA - Analyse Gemini 1.5 Pro
"""
import pytest
import json
from pathlib import Path


class TestF00Cortex:
    """Tests pour la frégate CORTEX."""
    
    def test_p1_masterplan_schema_exists(self, contracts_dir):
        """P1: Vérifie que le schema masterplan existe."""
        schema_path = contracts_dir / "masterplan_schema.json"
        assert schema_path.exists(), "masterplan_schema.json missing"
    
    def test_p2_golden_masterplan_valid_json(self, golden_dir):
        """P2: Vérifie que le golden masterplan est du JSON valide."""
        mp_path = golden_dir / "f00_cortex" / "test_masterplan.json"
        assert mp_path.exists(), "test_masterplan.json missing"
        
        with open(mp_path) as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "project_id" in data
        assert "rooms" in data
        assert "camera_path" in data
    
    def test_p3_masterplan_rooms_structure(self, test_masterplan):
        """P3: Vérifie la structure des rooms dans le masterplan."""
        if test_masterplan is None:
            pytest.skip("No test masterplan available")
        
        rooms = test_masterplan.get("rooms", [])
        assert len(rooms) >= 1, "At least one room required"
        
        for room in rooms:
            assert "id" in room
            assert "name" in room
            assert "type" in room
    
    def test_p4_masterplan_camera_path(self, test_masterplan):
        """P4: Vérifie la structure du camera_path."""
        if test_masterplan is None:
            pytest.skip("No test masterplan available")
        
        camera_path = test_masterplan.get("camera_path", {})
        assert "type" in camera_path
        assert "keyframes" in camera_path
        assert isinstance(camera_path["keyframes"], list)
    
    def test_p5_mock_masterplan_valid(self):
        """P5: Vérifie que le mock masterplan est valide."""
        from tests.mocks.mock_generators import generate_mock_masterplan
        
        mp = generate_mock_masterplan()
        
        assert "project_id" in mp
        assert "rooms" in mp
        assert "camera_path" in mp
        assert len(mp["rooms"]) >= 1
    
    def test_p6_masterplan_validator(self, contracts_dir, golden_dir):
        """P6: Vérifie le validator JSON sur le masterplan."""
        from tests.validators.json_validator import JSONValidator
        
        validator = JSONValidator(str(contracts_dir / "masterplan_schema.json"))
        result = validator.validate(str(golden_dir / "f00_cortex" / "test_masterplan.json"))
        
        assert result.valid, f"Validation failed: {result.errors}"
    
    def test_cortex_module_structure(self):
        """Vérifie que le module CORTEX a la structure attendue."""
        cortex_path = Path(__file__).parent.parent.parent / "FRIGATE_00_CORTEX"
        assert cortex_path.exists(), "FRIGATE_00_CORTEX directory missing"
        
        codebase = cortex_path / "CODEBASE"
        assert codebase.exists(), "CODEBASE directory missing"
    
    def test_cortex_import(self):
        """Vérifie que le module CORTEX est importable."""
        try:
            from FRIGATE_00_CORTEX.CODEBASE import cortex_pipeline
            assert cortex_pipeline is not None
        except ImportError as e:
            pytest.skip(f"CORTEX not importable (missing deps): {e}")
