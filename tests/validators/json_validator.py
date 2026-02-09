"""
EXODUS-SPECULUM - JSON Validator
Validator pour fichiers JSON (masterplan, spatial_data, etc.).
"""
import json
from pathlib import Path
from typing import Optional, List, Any
from .base_validator import BaseValidator, ValidationResult


class JSONValidator(BaseValidator):
    """
    Validator pour fichiers JSON avec support schema JSON Schema.
    
    Usage:
        validator = JSONValidator("contracts/masterplan_schema.json")
        result = validator.validate("golden/f00_cortex/test_masterplan.json")
    """
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        Valide un fichier JSON contre un schema optionnel.
        
        Args:
            file_path: Chemin vers le fichier JSON à valider
            
        Returns:
            ValidationResult avec statut et métriques
        """
        errors: List[str] = []
        warnings: List[str] = []
        metrics = {}
        
        if err := self._check_file_exists(file_path):
            return ValidationResult(valid=False, errors=[err])
        
        if err := self._check_extension(file_path, [".json"]):
            errors.append(err)
        
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
            
            metrics["keys"] = list(data.keys()) if isinstance(data, dict) else []
            metrics["size_kb"] = Path(file_path).stat().st_size / 1024
            metrics["type"] = type(data).__name__
            
            if isinstance(data, dict):
                metrics["key_count"] = len(data)
            elif isinstance(data, list):
                metrics["item_count"] = len(data)
            
            if self.contract:
                schema_errors = self._validate_against_schema(data)
                errors.extend(schema_errors)
                
                if "required" in self.contract:
                    for key in self.contract["required"]:
                        if isinstance(data, dict) and key not in data:
                            errors.append(f"Missing required key: {key}")
                            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {e.msg} at line {e.lineno}")
        except UnicodeDecodeError as e:
            errors.append(f"Encoding error: {e}")
        except Exception as e:
            errors.append(f"Unexpected error: {e}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_against_schema(self, data: Any) -> List[str]:
        """Valide les données contre un JSON Schema."""
        errors = []
        
        try:
            import jsonschema
            try:
                jsonschema.validate(data, self.contract)
            except jsonschema.ValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
                if e.path:
                    errors.append(f"  at path: {'.'.join(str(p) for p in e.path)}")
            except jsonschema.SchemaError as e:
                errors.append(f"Invalid schema: {e.message}")
        except ImportError:
            pass
        
        return errors
    
    def validate_structure(self, file_path: str, required_keys: List[str]) -> ValidationResult:
        """
        Valide qu'un JSON contient les clés requises.
        
        Args:
            file_path: Chemin vers le fichier JSON
            required_keys: Liste des clés requises au premier niveau
            
        Returns:
            ValidationResult
        """
        result = self.validate(file_path)
        if not result.valid:
            return result
        
        errors = []
        with open(file_path) as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            errors.append(f"Expected object, got {type(data).__name__}")
        else:
            for key in required_keys:
                if key not in data:
                    errors.append(f"Missing required key: {key}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            metrics=result.metrics
        )
