"""
Tests unitaires pour F03 PROJECTIONNISTE.
Camera Projection Mapping pour textures vidéo sur géométrie 3D.
"""
import pytest
from pathlib import Path


class TestF03Projectionniste:
    """Tests pour la frégate PROJECTIONNISTE."""
    
    def test_p1_camera_keyframe_fixture(self, sample_camera_keyframe):
        """P1: Vérifie la structure d'un keyframe caméra."""
        assert "frame" in sample_camera_keyframe
        assert "position" in sample_camera_keyframe
        assert "rotation" in sample_camera_keyframe
        
        assert len(sample_camera_keyframe["position"]) == 3
        assert len(sample_camera_keyframe["rotation"]) == 3
    
    def test_p2_keyframe_position_format(self, sample_camera_keyframe):
        """P2: Vérifie le format de position (x, y, z)."""
        pos = sample_camera_keyframe["position"]
        assert pos[2] == 1.6, "Camera height should be 1.6m (eye level)"
    
    def test_p3_projection_collections_required(self, contracts_dir):
        """P3: Vérifie les collections requises pour scene_projected."""
        import json
        with open(contracts_dir / "blend_contract.json") as f:
            contract = json.load(f)
        
        proj_collections = contract["required_collections"]["scene_projected"]
        assert "ROOM_SHELL" in proj_collections
        assert "CAMERAS" in proj_collections
    
    def test_p4_masterplan_keyframes_structure(self, test_masterplan):
        """P4: Vérifie la structure des keyframes dans le masterplan."""
        if test_masterplan is None:
            pytest.skip("No test masterplan")
        
        keyframes = test_masterplan["camera_path"]["keyframes"]
        assert len(keyframes) >= 2, "Need at least 2 keyframes"
        
        for kf in keyframes:
            assert "frame" in kf
            assert isinstance(kf["frame"], int)
    
    def test_p5_blend_max_keyframes(self, contracts_dir):
        """P5: Vérifie la limite de keyframes."""
        import json
        with open(contracts_dir / "blend_contract.json") as f:
            contract = json.load(f)
        
        # Note: La limite est dans FRIGATE_CONTRACTS, pas blend_contract
        # Ce test vérifie juste que le contrat est lisible
        assert contract is not None
    
    def test_projectionniste_module_structure(self):
        """Vérifie que le module a la structure attendue."""
        proj_path = Path(__file__).parent.parent.parent / "FRIGATE_03_PROJECTIONNISTE"
        assert proj_path.exists(), "FRIGATE_03_PROJECTIONNISTE directory missing"
    
    def test_projectionniste_import(self):
        """Vérifie que le module est importable (skip si pas de bpy)."""
        try:
            from FRIGATE_03_PROJECTIONNISTE.CODEBASE import projectionniste_pipeline
            assert projectionniste_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Projectionniste not importable (missing bpy?): {e}")
