"""
EXODUS-SPECULUM - Mock Torch
Mock pour PyTorch quand CUDA n'est pas disponible.

Permet d'exécuter des tests basiques sans GPU.
"""
from typing import Any, Optional, Tuple, List
import numpy as np


class MockTensor:
    """Mock d'un tensor PyTorch."""
    
    def __init__(self, data: np.ndarray):
        self._data = data
        self._device = "cpu"
    
    @property
    def shape(self) -> Tuple:
        return self._data.shape
    
    @property
    def dtype(self):
        return self._data.dtype
    
    def numpy(self) -> np.ndarray:
        return self._data
    
    def to(self, device: str) -> "MockTensor":
        self._device = device
        return self
    
    def cpu(self) -> "MockTensor":
        self._device = "cpu"
        return self
    
    def cuda(self) -> "MockTensor":
        self._device = "cuda:0"
        return self
    
    def squeeze(self, dim: int = None) -> "MockTensor":
        return MockTensor(np.squeeze(self._data, axis=dim))
    
    def unsqueeze(self, dim: int) -> "MockTensor":
        return MockTensor(np.expand_dims(self._data, axis=dim))
    
    def __repr__(self) -> str:
        return f"MockTensor(shape={self.shape}, device={self._device})"


class MockCuda:
    """Mock pour torch.cuda."""
    
    @staticmethod
    def is_available() -> bool:
        return False
    
    @staticmethod
    def device_count() -> int:
        return 0
    
    @staticmethod
    def empty_cache():
        pass
    
    @staticmethod
    def memory_allocated(device: int = 0) -> int:
        return 0
    
    @staticmethod
    def max_memory_allocated(device: int = 0) -> int:
        return 0


class MockTorch:
    """Mock du module torch."""
    
    cuda = MockCuda
    
    @staticmethod
    def tensor(data: Any, dtype=None) -> MockTensor:
        if isinstance(data, np.ndarray):
            return MockTensor(data)
        return MockTensor(np.array(data))
    
    @staticmethod
    def from_numpy(arr: np.ndarray) -> MockTensor:
        return MockTensor(arr.copy())
    
    @staticmethod
    def zeros(*size, dtype=None) -> MockTensor:
        return MockTensor(np.zeros(size))
    
    @staticmethod
    def ones(*size, dtype=None) -> MockTensor:
        return MockTensor(np.ones(size))
    
    @staticmethod
    def randn(*size) -> MockTensor:
        return MockTensor(np.random.randn(*size))
    
    @staticmethod
    def no_grad():
        """Context manager for no_grad (no-op in mock)."""
        class NoGrad:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return NoGrad()
    
    class nn:
        class Module:
            def __init__(self):
                self._training = True
            
            def eval(self):
                self._training = False
                return self
            
            def train(self, mode: bool = True):
                self._training = mode
                return self
            
            def to(self, device: str):
                return self
            
            def cuda(self):
                return self
            
            def cpu(self):
                return self
            
            def parameters(self):
                return []
            
            def state_dict(self):
                return {}
            
            def load_state_dict(self, state_dict):
                pass


def patch_torch():
    """
    Patch le module torch avec le mock.
    
    Usage:
        from tests.mocks.mock_torch import patch_torch
        patch_torch()
        import torch  # Now uses MockTorch
    """
    import sys
    sys.modules['torch'] = MockTorch
    return MockTorch
