"""
FRIGATE_01_SCANNER - Extraction données spatiales
FFmpeg, Depth Anything V2, YOLOv8, SAM
"""

from .scanner_pipeline import ScannerPipeline
from .frame_extractor import FrameExtractor
from .depth_estimator import DepthEstimator

__all__ = [
    'ScannerPipeline',
    'FrameExtractor',
    'DepthEstimator',
]
