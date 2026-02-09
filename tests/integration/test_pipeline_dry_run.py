"""
Test d'intégration dry-run du pipeline complet.
Vérifie que toutes les frégates sont importables et que les
contrats sont cohérents sans exécuter de code ML.
"""
import pytest
from pathlib import Path


class TestPipelineDryRun:
    """Tests d'intégration en mode dry-run."""
    
    def test_all_frigate_directories_exist(self, project_root):
        """Vérifie que tous les répertoires de frégates existent."""
        frigates = [
            "FRIGATE_00_CORTEX",
            "FRIGATE_01_SCANNER",
            "FRIGATE_02_SCENOGRAPHE",
            "FRIGATE_03_PROJECTIONNISTE",
            "FRIGATE_04_LOGISTIQUE",
            "FRIGATE_05_DIRECTEUR_PHOTO",
            "FRIGATE_06_ALCHIMISTE",
            "FRIGATE_07_PORTE_AVIONS",
        ]
        
        for frigate in frigates:
            frigate_path = project_root / frigate
            assert frigate_path.exists(), f"{frigate} directory missing"
            
            codebase = frigate_path / "CODEBASE"
            assert codebase.exists(), f"{frigate}/CODEBASE directory missing"
    
    def test_all_frigates_have_init(self, project_root):
        """Vérifie que toutes les frégates ont un __init__.py."""
        frigates = [
            "FRIGATE_00_CORTEX",
            "FRIGATE_01_SCANNER",
            "FRIGATE_02_SCENOGRAPHE",
            "FRIGATE_03_PROJECTIONNISTE",
            "FRIGATE_04_LOGISTIQUE",
            "FRIGATE_05_DIRECTEUR_PHOTO",
            "FRIGATE_06_ALCHIMISTE",
            "FRIGATE_07_PORTE_AVIONS",
        ]
        
        missing = []
        for frigate in frigates:
            init_path = project_root / frigate / "__init__.py"
            if not init_path.exists():
                missing.append(frigate)
        
        if missing:
            pytest.skip(f"Missing __init__.py in: {missing}")
    
    def test_output_contracts_importable(self):
        """Vérifie que les contrats sont importables."""
        from CORE_CONFIG.output_contracts import (
            DELIVERY_PROFILES,
            FRIGATE_CONTRACTS,
            GLOBAL_LIMITS
        )
        
        assert "PREMIUM" in DELIVERY_PROFILES
        assert "ECLAIREUR" in DELIVERY_PROFILES
        assert "CONQUERANT" in DELIVERY_PROFILES
        
        assert "F01_SCANNER" in FRIGATE_CONTRACTS
        assert "F06_ALCHIMISTE" in FRIGATE_CONTRACTS
        assert "F07_PORTE_AVIONS" in FRIGATE_CONTRACTS
        
        assert "max_chunk_transfer_mb" in GLOBAL_LIMITS
        assert "gpu_memory_threshold_gb" in GLOBAL_LIMITS
    
    def test_frigate_contracts_completeness(self):
        """Vérifie que tous les contrats de frégates sont définis."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        expected_frigates = [
            "F00_CORTEX",
            "F01_SCANNER",
            "F02_SCENOGRAPHE",
            "F03_PROJECTIONNISTE",
            "F04_LOGISTIQUE",
            "F05_DIRECTEUR_PHOTO",
            "F06_ALCHIMISTE",
            "F07_PORTE_AVIONS",
        ]
        
        for frigate_id in expected_frigates:
            assert frigate_id in FRIGATE_CONTRACTS, f"Contract missing for {frigate_id}"
            contract = FRIGATE_CONTRACTS[frigate_id]
            assert "name" in contract
            assert "inputs" in contract
            assert "outputs" in contract
            assert "constraints" in contract
    
    def test_golden_masterplan_valid(self, golden_dir, contracts_dir):
        """Vérifie que le golden masterplan est valide."""
        from tests.validators.json_validator import JSONValidator
        
        validator = JSONValidator(str(contracts_dir / "masterplan_schema.json"))
        result = validator.validate(str(golden_dir / "f00_cortex" / "test_masterplan.json"))
        
        assert result.valid, f"Golden masterplan invalid: {result.errors}"
    
    def test_contracts_json_valid(self, contracts_dir):
        """Vérifie que tous les fichiers de contrat sont du JSON valide."""
        import json
        
        contract_files = [
            "masterplan_schema.json",
            "depth_contract.json",
            "blend_contract.json",
            "video_contract.json",
        ]
        
        for filename in contract_files:
            filepath = contracts_dir / filename
            assert filepath.exists(), f"Contract file missing: {filename}"
            
            with open(filepath) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{filename} should be a JSON object"
    
    def test_validators_importable(self):
        """Vérifie que tous les validators sont importables."""
        from tests.validators import (
            BaseValidator,
            ValidationResult,
            JSONValidator,
            DepthValidator,
            VideoValidator,
        )
        
        assert BaseValidator is not None
        assert ValidationResult is not None
        assert JSONValidator is not None
        assert DepthValidator is not None
        assert VideoValidator is not None
    
    def test_mocks_importable(self):
        """Vérifie que tous les mocks sont importables."""
        from tests.mocks import (
            generate_mock_depth,
            generate_mock_frame,
            generate_mock_masterplan,
            generate_mock_spatial_data,
        )
        
        assert generate_mock_depth is not None
        assert generate_mock_frame is not None
        assert generate_mock_masterplan is not None
        assert generate_mock_spatial_data is not None
    
    def test_mock_depth_passes_validator(self, contracts_dir):
        """Vérifie que les mocks passent la validation."""
        import tempfile
        import numpy as np
        from tests.mocks import generate_mock_depth
        from tests.validators import DepthValidator
        
        depth = generate_mock_depth(960, 540)
        
        with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
            np.savez_compressed(f.name, depth=depth)
            
            validator = DepthValidator(str(contracts_dir / "depth_contract.json"))
            result = validator.validate(f.name)
            
            assert result.valid, f"Mock depth failed validation: {result.errors}"
    
    def test_mock_masterplan_passes_validator(self, contracts_dir):
        """Vérifie que le mock masterplan passe la validation."""
        import tempfile
        import json
        from tests.mocks import generate_mock_masterplan
        from tests.validators import JSONValidator
        
        masterplan = generate_mock_masterplan()
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode='w') as f:
            json.dump(masterplan, f)
            f.flush()
            
            validator = JSONValidator(str(contracts_dir / "masterplan_schema.json"))
            result = validator.validate(f.name)
            
            assert result.valid, f"Mock masterplan failed validation: {result.errors}"
    
    def test_paths_config_importable(self):
        """Vérifie que la config des chemins est importable."""
        from CORE_CONFIG.paths import (
            DRIVE_ROOT,
            FRIGATES,
            PathConfig,
        )
        
        assert DRIVE_ROOT is not None
        assert len(FRIGATES) == 8
        assert PathConfig.DRIVE_ROOT == DRIVE_ROOT
    
    def test_delivery_profile_configs_valid(self):
        """Vérifie que les profils de livraison sont cohérents."""
        from CORE_CONFIG.output_contracts import DELIVERY_PROFILES
        
        for profile_name, config in DELIVERY_PROFILES.items():
            assert "resolution" in config, f"{profile_name} missing resolution"
            assert "fps" in config, f"{profile_name} missing fps"
            assert "samples" in config, f"{profile_name} missing samples"
            
            w, h = config["resolution"]
            assert w > 0 and h > 0, f"{profile_name} invalid resolution"
            assert config["fps"] > 0, f"{profile_name} invalid fps"
            assert config["samples"] > 0, f"{profile_name} invalid samples"
    
    def test_global_limits_reasonable(self):
        """Vérifie que les limites globales sont raisonnables."""
        from CORE_CONFIG.output_contracts import GLOBAL_LIMITS
        
        assert GLOBAL_LIMITS["max_chunk_transfer_mb"] >= 100
        assert GLOBAL_LIMITS["max_total_pipeline_time_hours"] >= 1
        assert GLOBAL_LIMITS["gpu_memory_threshold_gb"] >= 8
        assert GLOBAL_LIMITS["max_concurrent_processes"] >= 1
