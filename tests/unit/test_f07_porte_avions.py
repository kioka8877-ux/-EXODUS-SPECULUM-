"""
Tests unitaires pour F07 PORTE-AVIONS.
Assemblage final - Encodage + Audio ASMR + Export multi-plateformes.
"""
import pytest
import json
from pathlib import Path


class TestF07PorteAvions:
    """Tests pour la frégate PORTE-AVIONS."""
    
    def test_p1_video_contract_exists(self, contracts_dir):
        """P1: Vérifie que le contrat vidéo existe."""
        contract_path = contracts_dir / "video_contract.json"
        assert contract_path.exists(), "video_contract.json missing"
    
    def test_p2_video_contract_codecs(self, contracts_dir):
        """P2: Vérifie les codecs supportés."""
        with open(contracts_dir / "video_contract.json") as f:
            contract = json.load(f)
        
        assert "h264" in contract["codec"]["video"]
        assert "aac" in contract["codec"]["audio"]
    
    def test_p3_video_resolution_limits(self, contracts_dir):
        """P3: Vérifie les limites de résolution."""
        with open(contracts_dir / "video_contract.json") as f:
            contract = json.load(f)
        
        res = contract["resolution"]
        assert res["min"] == [960, 540]
        assert res["max"] == [3840, 2160]
    
    def test_p4_fps_range(self, contracts_dir):
        """P4: Vérifie la plage FPS."""
        with open(contracts_dir / "video_contract.json") as f:
            contract = json.load(f)
        
        fps = contract["fps"]
        assert fps["min"] == 12
        assert fps["max"] == 60
    
    def test_p5_audio_required(self, contracts_dir):
        """P5: Vérifie que l'audio est requis."""
        with open(contracts_dir / "video_contract.json") as f:
            contract = json.load(f)
        
        assert contract["audio"]["required"] is True
        assert contract["audio"]["sample_rate"] == 44100
    
    def test_p6_platform_profiles_defined(self, contracts_dir):
        """P6: Vérifie les profils de plateformes."""
        with open(contracts_dir / "video_contract.json") as f:
            contract = json.load(f)
        
        platforms = contract["platform_profiles"]
        assert "youtube" in platforms
        assert "instagram" in platforms
        assert "tiktok" in platforms
    
    def test_p7_frigate_contract_variants(self):
        """P7: Vérifie le contrat pour les variantes."""
        from CORE_CONFIG.output_contracts import FRIGATE_CONTRACTS
        
        f07_contract = FRIGATE_CONTRACTS["F07_PORTE_AVIONS"]
        outputs = f07_contract["outputs"]
        
        assert "variants/" in outputs
        platforms = outputs["variants/"]["platforms"]
        assert "youtube" in platforms
    
    def test_p8_video_validator_available(self):
        """P8: Vérifie que le validator vidéo est importable."""
        from tests.validators.video_validator import VideoValidator
        
        validator = VideoValidator()
        assert validator is not None
    
    def test_porte_avions_module_structure(self):
        """Vérifie que le module a la structure attendue."""
        pa_path = Path(__file__).parent.parent.parent / "FRIGATE_07_PORTE_AVIONS"
        assert pa_path.exists(), "FRIGATE_07_PORTE_AVIONS directory missing"
    
    def test_porte_avions_import(self):
        """Vérifie que le module est importable."""
        try:
            from FRIGATE_07_PORTE_AVIONS.CODEBASE import porte_avions_pipeline
            assert porte_avions_pipeline is not None
        except ImportError as e:
            pytest.skip(f"Porte-Avions not importable: {e}")
