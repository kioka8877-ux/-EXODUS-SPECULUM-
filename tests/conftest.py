"""
EXODUS-SPECULUM - Configuration pytest globale
Phase 2.5B: Golden Samples & Test Framework

Ce fichier configure les fixtures partagées pour tous les tests.
"""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES GLOBALES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def golden_dir():
    """Retourne le chemin vers les golden samples."""
    return Path(__file__).parent / "golden"

@pytest.fixture
def contracts_dir():
    """Retourne le chemin vers les contracts JSON."""
    return Path(__file__).parent / "contracts"

@pytest.fixture
def mock_mode():
    """Indique si on est en mode mock (pas de ML réel)."""
    return True

@pytest.fixture
def project_root():
    """Retourne le chemin vers la racine du projet."""
    return PROJECT_ROOT

@pytest.fixture
def test_masterplan(golden_dir):
    """Charge le masterplan de test."""
    import json
    mp_path = golden_dir / "f00_cortex" / "test_masterplan.json"
    if mp_path.exists():
        with open(mp_path) as f:
            return json.load(f)
    return None

@pytest.fixture
def sample_room_dimensions():
    """Dimensions de test pour une pièce standard."""
    return {
        "width": 5.0,
        "length": 6.0,
        "height": 2.8
    }

@pytest.fixture
def sample_camera_keyframe():
    """Keyframe de test pour caméra."""
    return {
        "frame": 0,
        "position": [0, 0, 1.6],
        "rotation": [90, 0, 0]
    }

# ═══════════════════════════════════════════════════════════════════════════
# MARKERS
# ═══════════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "gpu: marks tests requiring GPU")
    config.addinivalue_line("markers", "blender: marks tests requiring Blender/bpy")
    config.addinivalue_line("markers", "ml: marks tests requiring ML models")

# ═══════════════════════════════════════════════════════════════════════════
# SKIP CONDITIONS
# ═══════════════════════════════════════════════════════════════════════════

def has_bpy():
    """Check if bpy (Blender Python) is available."""
    try:
        import bpy
        return True
    except ImportError:
        return False

def has_torch():
    """Check if PyTorch is available."""
    try:
        import torch
        return True
    except ImportError:
        return False

def has_cuda():
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

skip_no_bpy = pytest.mark.skipif(not has_bpy(), reason="bpy not available")
skip_no_torch = pytest.mark.skipif(not has_torch(), reason="PyTorch not available")
skip_no_cuda = pytest.mark.skipif(not has_cuda(), reason="CUDA not available")
