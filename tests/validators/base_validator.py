"""
EXODUS-SPECULUM - Base Validator
Classe de base pour tous les validators du test framework.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import json


class ValidationResult:
    """Résultat d'une validation avec statut, erreurs et métriques."""
    
    def __init__(
        self,
        valid: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.metrics = metrics or {}
    
    def __bool__(self) -> bool:
        return self.valid
    
    def __repr__(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        return f"ValidationResult({status}, errors={len(self.errors)}, warnings={len(self.warnings)})"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }
    
    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge deux résultats de validation."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            metrics={**self.metrics, **other.metrics},
        )


class BaseValidator:
    """
    Classe de base pour les validators.
    
    Usage:
        validator = SomeValidator(contract_path="path/to/contract.json")
        result = validator.validate("path/to/file")
        if result.valid:
            print("OK")
        else:
            print(result.errors)
    """
    
    def __init__(self, contract_path: Optional[str] = None):
        """
        Initialise le validator avec un contrat optionnel.
        
        Args:
            contract_path: Chemin vers le fichier JSON de contrat
        """
        self.contract = None
        self.contract_path = contract_path
        
        if contract_path and Path(contract_path).exists():
            with open(contract_path) as f:
                self.contract = json.load(f)
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        Valide un fichier.
        
        Args:
            file_path: Chemin vers le fichier à valider
            
        Returns:
            ValidationResult avec statut et détails
            
        Raises:
            NotImplementedError: Doit être implémenté par les sous-classes
        """
        raise NotImplementedError("Subclasses must implement validate()")
    
    def _check_file_exists(self, file_path: str) -> Optional[str]:
        """Vérifie que le fichier existe."""
        if not Path(file_path).exists():
            return f"File not found: {file_path}"
        return None
    
    def _check_file_size(self, file_path: str, min_kb: float = 0, max_kb: float = float('inf')) -> Optional[str]:
        """Vérifie la taille du fichier."""
        size_kb = Path(file_path).stat().st_size / 1024
        if size_kb < min_kb:
            return f"File too small: {size_kb:.1f}KB < {min_kb}KB"
        if size_kb > max_kb:
            return f"File too large: {size_kb:.1f}KB > {max_kb}KB"
        return None
    
    def _check_extension(self, file_path: str, allowed: List[str]) -> Optional[str]:
        """Vérifie l'extension du fichier."""
        ext = Path(file_path).suffix.lower()
        allowed_lower = [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in allowed]
        if ext not in allowed_lower:
            return f"Invalid extension: {ext}, allowed: {allowed_lower}"
        return None
