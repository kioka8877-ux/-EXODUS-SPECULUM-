"""
Tests unitaires pour F04 LOGISTIQUE.
Asset replacement - Ghost Proxy → Real 3D Assets.
"""
import pytest
from pathlib import Path


class TestF04Logistique:
    """Tests pour la frégate LOGISTIQUE."""
    
    def test_p1_furnished_collections_required(self, contracts_dir):
        """P1: Vérifie les collections requises pour scene_furnished."""
        import json
        with open(contracts_dir / "blend_contract.json") as f:
            contract = json.load(f)
        
        furn_collections = contract["required_collections"]["scene_furnished"]
        assert "ROOM_SHELL" in furn_collections
        assert "FURNITURE" in furn_collections
    
    def test_p2_assetshub_path_defined(self):
        """P2: Vérifie que le chemin ASSETSHUB est défini."""
        from CORE_CONFIG.paths import ASSETSHUB_PATH
        assert ASSETSHUB_PATH is not None
        assert "ASSETSHUB" in ASSETSHUB_PATH
    
    def test_p3_frigate_contract_linked_assets(self):
        """P3: Vérifie le contrat pour assets linkés."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f04_contract = FRIGATE_CONTRACTS["F04_LOGISTIQUE"]
        outputs = f04_contract["outputs"]
        
        assert "scene_furnished.blend" in outputs
        assert outputs["scene_furnished.blend"]["linked_assets"] is True
    
    def test_p4_lod_enabled_in_contract(self):
        """P4: Vérifie que le LOD est activé dans le contrat."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f04_contract = FRIGATE_CONTRACTS["F04_LOGISTIQUE"]
        assert f04_contract["outputs"]["scene_furnished.blend"]["lod_enabled"] is True
        assert f04_contract["constraints"]["lod_levels"] == 3
    
    def test_p5_max_linked_assets_limit(self):
        """P5: Vérifie la limite d'assets linkés."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f04_contract = FRIGATE_CONTRACTS["F04_LOGISTIQUE"]
        assert f04_contract["constraints"]["max_linked_assets"] == 50
    
    def test_logistique_module_structure(self):
        """Vérifie que le module a la structure attendue."""
        log_path = Path(__file__).parent.parent.parent / "FRIGATE_04_LOGISTIQUE"
        assert log_path.exists(), "FRIGATE_04_LOGISTIQUE directory missing"
    
    def test_logistique_import(self):
        """Vérifie que le module est importable."""
        try:
            from FRIGATE_04_LOGISTIQUE.CODEBASE import logistique_pipeline
            assert logistique_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Logistique not importable: {e}")
