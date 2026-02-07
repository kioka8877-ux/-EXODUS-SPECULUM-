#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Script d'installation des dépendances
========================================================
Ce script installe toutes les dépendances requises pour le pipeline SPECULUM.

Usage sur Google Colab:
    !python scripts/install_dependencies.py

Usage local (non recommandé):
    python scripts/install_dependencies.py

Auteur: Vulkan, Maître de la Forge
Date: 2026-02-06
"""

import subprocess
import sys
import os

DEPENDENCIES = {
    "core": [
        ("torch>=2.0.0", "PyTorch - Framework ML principal"),
        ("torchvision", "TorchVision - Utilitaires vision"),
        ("numpy", "NumPy - Calcul numérique"),
        ("opencv-python", "OpenCV - Traitement d'images"),
        ("pillow", "Pillow - Manipulation d'images"),
    ],
    "blender": [
        ("bpy==4.0.0", "Blender Python API - Rendu 3D headless"),
    ],
    "ai_models": [
        # À activer dans Phase 1
        # ("ultralytics", "YOLOv8 - Détection d'objets"),
        # ("segment-anything", "SAM - Segmentation"),
        # ("google-generativeai", "Gemini API - Vision IA"),
    ],
    "upscaling": [
        # À activer dans Phase 2
        # ("realesrgan", "Real-ESRGAN - Upscaling 4x"),
    ],
    "video": [
        # À activer dans Phase 3
        # ("ffmpeg-python", "FFmpeg bindings"),
    ],
    "utilities": [
        ("tqdm", "TQDM - Barres de progression"),
        ("pyyaml", "PyYAML - Parsing configuration"),
    ]
}

SYSTEM_PACKAGES = [
    "libxi6",
    "libxxf86vm1", 
    "libxfixes3",
    "libxrender1",
    "libgl1",
]


def run_command(cmd, description=""):
    """Exécute une commande shell et capture le résultat."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def install_system_packages():
    """Installe les packages système requis (Linux/Colab)."""
    print("\n📦 PACKAGES SYSTÈME")
    print("-" * 40)
    
    if sys.platform != "linux":
        print("  ⚠️ Skip (non-Linux)")
        return True
    
    # Check if running as root or with sudo
    if os.geteuid() != 0:
        print("  ⚠️ Skip (pas root, installer manuellement)")
        return True
    
    # Update package list
    success, _ = run_command("apt-get update -qq")
    if not success:
        print("  ❌ apt-get update failed")
        return False
    
    # Install packages
    packages_str = " ".join(SYSTEM_PACKAGES)
    success, output = run_command(f"apt-get install -qq -y {packages_str}")
    
    if success:
        print(f"  ✅ {len(SYSTEM_PACKAGES)} packages installés")
    else:
        print(f"  ❌ Installation échouée: {output}")
        return False
    
    return True


def install_pip_package(package_spec):
    """Installe un package pip."""
    cmd = f"{sys.executable} -m pip install -q {package_spec}"
    success, output = run_command(cmd)
    return success


def install_python_packages():
    """Installe tous les packages Python."""
    total_installed = 0
    total_failed = 0
    
    for category, packages in DEPENDENCIES.items():
        if not packages:  # Skip empty categories
            continue
            
        print(f"\n📦 {category.upper()}")
        print("-" * 40)
        
        for item in packages:
            if isinstance(item, tuple):
                pkg_spec, description = item
            else:
                pkg_spec = item
                description = ""
            
            # Extract package name for display
            pkg_name = pkg_spec.split(">=")[0].split("==")[0].split("[")[0]
            
            success = install_pip_package(pkg_spec)
            
            if success:
                print(f"  ✅ {pkg_name}")
                total_installed += 1
            else:
                print(f"  ❌ {pkg_name}")
                total_failed += 1
    
    return total_installed, total_failed


def verify_critical_imports():
    """Vérifie que les imports critiques fonctionnent."""
    print("\n🔍 VÉRIFICATION IMPORTS CRITIQUES")
    print("-" * 40)
    
    critical_checks = [
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("bpy", "Blender"),
    ]
    
    all_ok = True
    for module, name in critical_checks:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_ok = False
    
    return all_ok


def check_gpu():
    """Vérifie la disponibilité GPU."""
    print("\n🎮 VÉRIFICATION GPU")
    print("-" * 40)
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"  ✅ GPU: {gpu_name}")
            print(f"  ✅ VRAM: {vram:.1f} GB")
            print(f"  ✅ CUDA: {torch.version.cuda}")
            return True
        else:
            print("  ⚠️ Pas de GPU CUDA détecté")
            return False
    except ImportError:
        print("  ❌ PyTorch non disponible")
        return False


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("     EXODUS-SPECULUM - Installation Dépendances")
    print("=" * 60)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    
    # Install system packages (Colab/Linux only)
    install_system_packages()
    
    # Install Python packages
    installed, failed = install_python_packages()
    
    # Verify critical imports
    imports_ok = verify_critical_imports()
    
    # Check GPU
    gpu_ok = check_gpu()
    
    # Summary
    print("\n" + "=" * 60)
    print("                    RÉSUMÉ")
    print("=" * 60)
    print(f"  Packages installés: {installed}")
    print(f"  Packages échoués: {failed}")
    print(f"  Imports critiques: {'✅ OK' if imports_ok else '❌ ERREURS'}")
    print(f"  GPU: {'✅ Disponible' if gpu_ok else '⚠️ Non disponible'}")
    print("=" * 60)
    
    if failed > 0 or not imports_ok:
        print("⚠️ INSTALLATION INCOMPLÈTE - Vérifier les erreurs ci-dessus")
        return 1
    else:
        print("✅ INSTALLATION TERMINÉE AVEC SUCCÈS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
