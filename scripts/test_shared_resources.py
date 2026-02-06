#!/usr/bin/env python3
"""
EXODUS-SPECULUM - Test des Ressources Partagées
Usage: !python scripts/test_shared_resources.py

Ce script valide:
1. L'accès aux ressources partagées sur Google Drive
2. Le chargement des modèles IA (Depth Anything V2)
3. Le Library Linking Blender depuis Drive
4. Les latences de ces opérations
"""

import os
import sys
import time
import json

# Configuration
SHARED_RESOURCES = "/content/drive/MyDrive/EXODUS_SHARED_RESOURCES"
AI_MODELS_PATH = os.path.join(SHARED_RESOURCES, "AI_MODELS")
ASSETS_HUB_PATH = os.path.join(SHARED_RESOURCES, "ASSETS_HUB")

LATENCY_REPORT = {
    "timestamp": None,
    "tests": []
}

def test_path_exists(path, name):
    """Test si un chemin existe"""
    exists = os.path.exists(path)
    print(f"{'✅' if exists else '❌'} {name}: {path}")
    return exists

def test_model_load(model_path, model_name):
    """Test chargement d'un modèle avec mesure de latence"""
    import torch
    
    print(f"\n⏱️ Test chargement: {model_name}")
    
    if not os.path.exists(model_path):
        print(f"  ❌ Fichier non trouvé")
        return None
    
    start = time.time()
    try:
        state_dict = torch.load(model_path, map_location='cpu')
        latency = time.time() - start
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        
        print(f"  ✅ Chargé en {latency:.2f}s ({size_mb:.0f} MB)")
        
        del state_dict
        torch.cuda.empty_cache()
        
        return {
            "name": model_name,
            "path": model_path,
            "size_mb": size_mb,
            "latency_seconds": latency,
            "status": "success"
        }
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return {
            "name": model_name,
            "path": model_path,
            "error": str(e),
            "status": "failed"
        }

def test_blender_linking(blend_path, object_name="TestObject"):
    """Test Library Linking Blender depuis Drive"""
    import bpy
    
    print(f"\n🔗 Test Blender Library Linking")
    print(f"   Source: {blend_path}")
    
    if not os.path.exists(blend_path):
        print(f"  ⚠️ Fichier non trouvé, création d'un asset de test...")
        
        # Créer un .blend de test
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.name = "TestCube_AssetHub"
        
        # Ajouter custom properties
        cube["asset_type"] = "furniture"
        cube["asset_category"] = "test"
        cube["is_ghost_proxy"] = True
        
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(blend_path), exist_ok=True)
        
        # Sauvegarder
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"  ✅ Asset de test créé: {blend_path}")
    
    # Test de linking
    start = time.time()
    try:
        # Reset scene
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        # Link depuis le fichier externe
        with bpy.data.libraries.load(blend_path, link=True) as (data_from, data_to):
            # Lister les objets disponibles
            print(f"  📦 Objets disponibles: {data_from.objects}")
            if data_from.objects:
                data_to.objects = [data_from.objects[0]]
        
        latency = time.time() - start
        
        # Vérifier le link
        if data_to.objects and data_to.objects[0]:
            linked_obj = data_to.objects[0]
            
            # Ajouter à la scène
            bpy.context.collection.objects.link(linked_obj)
            
            print(f"  ✅ Linking réussi en {latency:.2f}s")
            print(f"     Objet linké: {linked_obj.name}")
            
            # Vérifier custom properties
            if linked_obj.get("is_ghost_proxy"):
                print(f"     → Ghost Proxy détecté!")
                print(f"     → Type: {linked_obj.get('asset_type', 'unknown')}")
            
            return {
                "blend_file": blend_path,
                "object_linked": linked_obj.name,
                "latency_seconds": latency,
                "custom_properties_preserved": bool(linked_obj.get("is_ghost_proxy")),
                "status": "success"
            }
        else:
            print(f"  ❌ Aucun objet linké")
            return {"status": "failed", "error": "No objects linked"}
            
    except Exception as e:
        print(f"  ❌ Erreur linking: {e}")
        return {"status": "failed", "error": str(e)}

def main():
    from datetime import datetime
    
    print("=" * 60)
    print("EXODUS-SPECULUM - Test Ressources Partagées")
    print("=" * 60)
    
    LATENCY_REPORT["timestamp"] = datetime.now().isoformat()
    
    # 1. Test existence des chemins
    print("\n📁 Vérification structure Drive:")
    test_path_exists(SHARED_RESOURCES, "SHARED_RESOURCES")
    test_path_exists(AI_MODELS_PATH, "AI_MODELS")
    test_path_exists(ASSETS_HUB_PATH, "ASSETS_HUB")
    
    # Créer structure si manquante
    for path in [AI_MODELS_PATH, ASSETS_HUB_PATH]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"  📁 Créé: {path}")
    
    # 2. Test chargement modèle IA
    depth_model_dir = os.path.join(AI_MODELS_PATH, "depth_anything_v2")
    if os.path.exists(depth_model_dir):
        model_files = [f for f in os.listdir(depth_model_dir) 
                       if f.endswith(('.pth', '.safetensors', '.pt'))]
        if model_files:
            model_path = os.path.join(depth_model_dir, model_files[0])
            result = test_model_load(model_path, "Depth Anything V2")
            if result:
                LATENCY_REPORT["tests"].append(result)
        else:
            print(f"\n⚠️ Aucun fichier modèle dans: {depth_model_dir}")
            print("   Fichiers attendus: .pth, .safetensors, .pt")
            print("   Télécharger depuis: https://huggingface.co/depth-anything/Depth-Anything-V2-Large")
    else:
        print(f"\n⚠️ Dossier Depth Anything V2 non trouvé")
        print(f"   Créer: {depth_model_dir}")
        os.makedirs(depth_model_dir, exist_ok=True)
        LATENCY_REPORT["tests"].append({
            "name": "Depth Anything V2",
            "status": "skipped",
            "reason": "Model not downloaded"
        })
    
    # 3. Test Blender Library Linking
    test_blend = os.path.join(ASSETS_HUB_PATH, "test_asset.blend")
    result = test_blender_linking(test_blend)
    if result:
        LATENCY_REPORT["tests"].append(result)
    
    # 4. Rapport final
    print("\n" + "=" * 60)
    print("RAPPORT DE LATENCE")
    print("=" * 60)
    
    for test in LATENCY_REPORT["tests"]:
        if test["status"] == "success":
            latency = test.get("latency_seconds", 0)
            status = "🚀 EXCELLENT" if latency < 10 else "✅ OK" if latency < 30 else "⚠️ LENT"
            name = test.get('name', test.get('blend_file', 'Unknown'))
            print(f"  {name}: {latency:.2f}s [{status}]")
        elif test["status"] == "skipped":
            print(f"  {test.get('name', 'Unknown')}: ⏭️ IGNORÉ - {test.get('reason', 'Unknown')}")
        else:
            print(f"  {test.get('name', 'Unknown')}: ❌ ÉCHEC - {test.get('error', 'Unknown error')}")
    
    # Sauvegarder rapport JSON
    report_path = "/content/latency_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(LATENCY_REPORT, f, indent=2)
        print(f"\n📊 Rapport sauvegardé: {report_path}")
    except Exception as e:
        print(f"\n⚠️ Impossible de sauvegarder le rapport: {e}")
    
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
