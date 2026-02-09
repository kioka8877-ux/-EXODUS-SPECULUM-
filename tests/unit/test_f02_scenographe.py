"""
Tests unitaires pour F02 SCÉNOGRAPHE.
Génération géométrie 3D (blob room + proxies).
"""
import pytest
from pathlib import Path


class TestF02Scenographe:
    """Tests pour la frégate SCÉNOGRAPHE."""
    
    def test_p1_blend_contract_exists(self, contracts_dir):
        """P1: Vérifie que le contrat blend existe."""
        import json
        contract_path = contracts_dir / "blend_contract.json"
        assert contract_path.exists(), "blend_contract.json missing"
        
        with open(contract_path) as f:
            contract = json.load(f)
        
        assert "required_collections" in contract
        assert "scene_shell" in contract["required_collections"]
    
    def test_p2_required_collections_defined(self, contracts_dir):
        """P2: Vérifie les collections requises pour scene_shell."""
        import json
        with open(contracts_dir / "blend_contract.json") as f:
            contract = json.load(f)
        
        scene_shell_collections = contract["required_collections"]["scene_shell"]
        assert "ROOM_SHELL" in scene_shell_collections
        assert "PROXIES" in scene_shell_collections
    
    def test_p3_mock_scene_structure(self):
        """P3: Vérifie la structure d'une scène mock."""
        from tests.mocks.mock_bpy import create_mock_scene
        
        scene = create_mock_scene()
        
        assert scene.name == "TestScene"
        assert len(scene.collection.children) >= 2
        
        collection_names = [c.name for c in scene.collection.children]
        assert "ROOM_SHELL" in collection_names
        assert "PROXIES" in collection_names
    
    def test_p4_mock_scene_has_camera(self):
        """P4: Vérifie que la scène mock a une caméra."""
        from tests.mocks.mock_bpy import create_mock_scene
        
        scene = create_mock_scene()
        
        assert scene.camera is not None
        assert scene.camera.type == "CAMERA"
        assert scene.camera.location.z == 1.6
    
    def test_p5_room_dimensions_fixture(self, sample_room_dimensions):
        """P5: Vérifie les dimensions de test."""
        assert sample_room_dimensions["width"] == 5.0
        assert sample_room_dimensions["length"] == 6.0
        assert sample_room_dimensions["height"] == 2.8
    
    def test_scenographe_module_structure(self):
        """Vérifie que le module SCÉNOGRAPHE a la structure attendue."""
        sceno_path = Path(__file__).parent.parent.parent / "FRIGATE_02_SCENOGRAPHE"
        assert sceno_path.exists(), "FRIGATE_02_SCENOGRAPHE directory missing"
    
    def test_scenographe_import(self):
        """Vérifie que le module est importable (skip si pas de bpy)."""
        try:
            from FRIGATE_02_SCENOGRAPHE.CODEBASE import scenographe_pipeline
            assert scenographe_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Scenographe not importable (missing bpy?): {e}")
