#!/usr/bin/env python3
"""
FRIGATE_01_SCANNER - Extraction vidéo, depth estimation, détection et segmentation.
FFmpeg extraction + Depth Anything V2 + YOLOv8 + SAM.
"""

from .scanner_pipeline import ScannerPipeline, run_scanner
from .frame_extractor import FrameExtractor, extract_frames_from_video
from .depth_estimator import DepthEstimator, estimate_depth_for_frames
from .object_detector import ObjectDetector, detect_objects_in_image, REAL_ESTATE_CLASSES
from .segmenter import SAMSegmenter, segment_from_detection, SAM_MODELS

__all__ = [
    'ScannerPipeline',
    'run_scanner',
    'FrameExtractor',
    'extract_frames_from_video',
    'DepthEstimator',
    'estimate_depth_for_frames',
    'ObjectDetector',
    'detect_objects_in_image',
    'REAL_ESTATE_CLASSES',
    'SAMSegmenter',
    'segment_from_detection',
    'SAM_MODELS',
]
