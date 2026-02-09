"""
Tests unitaires pour F01 SCANNER.
Extraction vidéo et depth estimation.
"""
import pytest
import numpy as np
from pathlib import Path


class TestF01Scanner:
    """Tests pour la frégate SCANNER."""
    
    def test_p1_depth_contract_format(self, contracts_dir):
        """P1: Vérifie que le contrat depth est valide."""
        import json
        contract_path = contracts_dir / "depth_contract.json"
        assert contract_path.exists(), "depth_contract.json missing"
        
        with open(contract_path) as f:
            contract = json.load(f)
        
        assert "dtype" in contract
        assert contract["dtype"] == "uint16"
        assert "resolution" in contract
        assert "value_range" in contract
    
    def test_p2_mock_depth_format(self):
        """P2: Vérifie que le mock depth respecte le format uint16."""
        from tests.mocks.mock_generators import generate_mock_depth
        
        depth = generate_mock_depth(960, 540)
        
        assert depth.dtype == np.uint16
        assert depth.shape == (540, 960)
        assert depth.min() >= 0
        assert depth.max() <= 65535
    
    def test_p3_depth_distribution(self):
        """P3: Vérifie que la depth a une distribution réaliste."""
        from tests.mocks.mock_generators import generate_mock_depth
        
        depth = generate_mock_depth()
        
        assert np.std(depth) > 1000, "Depth should have significant variation"
        assert 5000 < np.mean(depth) < 60000, "Mean depth should be in reasonable range"
    
    def test_p4_depth_validator(self, contracts_dir):
        """P4: Vérifie le validator depth sur données mock."""
        from tests.mocks.mock_generators import generate_mock_depth
        from tests.validators.depth_validator import DepthValidator
        import tempfile
        
        depth = generate_mock_depth(960, 540)
        
        with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
            np.savez_compressed(f.name, depth=depth)
            
            validator = DepthValidator(str(contracts_dir / "depth_contract.json"))
            result = validator.validate(f.name)
            
            assert result.valid, f"Depth validation failed: {result.errors}"
            assert "shape" in result.metrics
            assert result.metrics["dtype"] == "uint16"
    
    def test_p5_mock_frame_format(self):
        """P5: Vérifie que le mock frame est un RGB valide."""
        from tests.mocks.mock_generators import generate_mock_frame
        
        frame = generate_mock_frame(960, 540)
        
        assert frame.dtype == np.uint8
        assert frame.shape == (540, 960, 3)
        assert frame.min() >= 0
        assert frame.max() <= 255
    
    def test_scanner_module_structure(self):
        """Vérifie que le module SCANNER a la structure attendue."""
        scanner_path = Path(__file__).parent.parent.parent / "FRIGATE_01_SCANNER"
        assert scanner_path.exists(), "FRIGATE_01_SCANNER directory missing"
        
        codebase = scanner_path / "CODEBASE"
        assert codebase.exists(), "CODEBASE directory missing"
    
    def test_scanner_import(self):
        """Vérifie que le module SCANNER est importable."""
        try:
            from FRIGATE_01_SCANNER.CODEBASE import scanner_pipeline
            assert scanner_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Scanner not importable (missing deps): {e}")
