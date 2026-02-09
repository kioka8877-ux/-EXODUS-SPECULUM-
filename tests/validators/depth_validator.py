"""
EXODUS-SPECULUM - Depth Validator
Validator pour depth maps 16-bit (F01 SCANNER output).
"""
from pathlib import Path
from typing import Optional, List
from .base_validator import BaseValidator, ValidationResult


class DepthValidator(BaseValidator):
    """
    Validator pour depth maps PNG 16-bit.
    
    Vérifie:
    - Format PNG 16-bit grayscale
    - Résolution dans les limites
    - Plage de valeurs [0, 65535]
    - Taille de fichier raisonnable
    
    Usage:
        validator = DepthValidator("contracts/depth_contract.json")
        result = validator.validate("depth_maps/depth_000001.png")
    """
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        Valide une depth map.
        
        Args:
            file_path: Chemin vers le fichier PNG de depth
            
        Returns:
            ValidationResult avec métriques de la depth map
        """
        errors: List[str] = []
        warnings: List[str] = []
        metrics = {}
        
        if err := self._check_file_exists(file_path):
            return ValidationResult(valid=False, errors=[err])
        
        if err := self._check_extension(file_path, [".png", ".npz"]):
            errors.append(err)
        
        try:
            import numpy as np
            
            ext = Path(file_path).suffix.lower()
            
            if ext == ".npz":
                data = np.load(file_path)
                if 'depth' in data:
                    depth = data['depth']
                else:
                    depth = data[list(data.keys())[0]]
            else:
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    depth = np.array(img)
                except ImportError:
                    import cv2
                    depth = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            
            metrics["shape"] = depth.shape
            metrics["dtype"] = str(depth.dtype)
            metrics["min_value"] = int(depth.min())
            metrics["max_value"] = int(depth.max())
            metrics["mean_value"] = float(depth.mean())
            metrics["std_value"] = float(depth.std())
            metrics["size_kb"] = Path(file_path).stat().st_size / 1024
            
            if self.contract:
                expected_dtype = self.contract.get("dtype", "uint16")
                if str(depth.dtype) != expected_dtype:
                    errors.append(f"Wrong dtype: {depth.dtype}, expected {expected_dtype}")
                
                value_range = self.contract.get("value_range", {})
                if depth.min() < value_range.get("min", 0):
                    errors.append(f"Values below minimum: {depth.min()} < {value_range['min']}")
                if depth.max() > value_range.get("max", 65535):
                    errors.append(f"Values above maximum: {depth.max()} > {value_range['max']}")
                
                res = self.contract.get("resolution", {})
                if "min" in res:
                    min_res = res["min"]
                    if depth.shape[1] < min_res[0] or depth.shape[0] < min_res[1]:
                        errors.append(f"Resolution too low: {depth.shape}, min: {min_res}")
                if "max" in res:
                    max_res = res["max"]
                    if depth.shape[1] > max_res[0] or depth.shape[0] > max_res[1]:
                        errors.append(f"Resolution too high: {depth.shape}, max: {max_res}")
                
                size_limits = self.contract.get("file_size_kb", {})
                size_kb = metrics["size_kb"]
                if size_kb < size_limits.get("min", 0):
                    warnings.append(f"File unusually small: {size_kb:.1f}KB")
                if size_kb > size_limits.get("max", float('inf')):
                    errors.append(f"File too large: {size_kb:.1f}KB")
            
            if len(depth.shape) != 2:
                errors.append(f"Expected 2D array, got shape {depth.shape}")
            
            if metrics["std_value"] < 100:
                warnings.append(f"Low variance in depth values (std={metrics['std_value']:.1f}), may be flat")
                
        except ImportError as e:
            errors.append(f"Missing dependency: {e}")
        except Exception as e:
            errors.append(f"Error reading depth map: {e}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def validate_batch(self, directory: str, pattern: str = "depth_*.png") -> ValidationResult:
        """
        Valide un répertoire de depth maps.
        
        Args:
            directory: Chemin vers le répertoire
            pattern: Glob pattern pour les fichiers
            
        Returns:
            ValidationResult agrégé
        """
        import glob
        
        dir_path = Path(directory)
        if not dir_path.exists():
            return ValidationResult(valid=False, errors=[f"Directory not found: {directory}"])
        
        files = list(dir_path.glob(pattern))
        if not files:
            return ValidationResult(valid=False, errors=[f"No files matching {pattern} in {directory}"])
        
        all_errors = []
        all_warnings = []
        metrics = {
            "file_count": len(files),
            "total_size_mb": 0,
            "resolutions": set(),
        }
        
        for f in files:
            result = self.validate(str(f))
            if not result.valid:
                all_errors.extend([f"{f.name}: {e}" for e in result.errors])
            all_warnings.extend([f"{f.name}: {w}" for w in result.warnings])
            metrics["total_size_mb"] += result.metrics.get("size_kb", 0) / 1024
            if "shape" in result.metrics:
                metrics["resolutions"].add(result.metrics["shape"])
        
        metrics["resolutions"] = list(metrics["resolutions"])
        metrics["consistent_resolution"] = len(metrics["resolutions"]) == 1
        
        return ValidationResult(
            valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            metrics=metrics
        )
