"""
EXODUS-SPECULUM - Mock Blender (bpy)
Mock pour Blender Python API quand Blender n'est pas disponible.

Permet d'exécuter des tests basiques sans installation Blender.
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class MockVector:
    """Mock de mathutils.Vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __iter__(self):
        return iter([self.x, self.y, self.z])
    
    def __getitem__(self, index):
        return [self.x, self.y, self.z][index]
    
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value


@dataclass
class MockObject:
    """Mock d'un objet Blender."""
    name: str = "Object"
    type: str = "MESH"
    location: MockVector = field(default_factory=MockVector)
    rotation_euler: MockVector = field(default_factory=MockVector)
    scale: MockVector = field(default_factory=lambda: MockVector(1, 1, 1))
    data: Any = None
    parent: Optional["MockObject"] = None
    children: List["MockObject"] = field(default_factory=list)
    _custom_props: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str):
        return self._custom_props.get(key)
    
    def __setitem__(self, key: str, value: Any):
        self._custom_props[key] = value


@dataclass
class MockCollection:
    """Mock d'une collection Blender."""
    name: str = "Collection"
    objects: List[MockObject] = field(default_factory=list)
    children: List["MockCollection"] = field(default_factory=list)
    
    def link(self, obj: MockObject):
        self.objects.append(obj)
    
    def unlink(self, obj: MockObject):
        if obj in self.objects:
            self.objects.remove(obj)


@dataclass
class MockScene:
    """Mock d'une scène Blender."""
    name: str = "Scene"
    frame_start: int = 1
    frame_end: int = 250
    frame_current: int = 1
    collection: MockCollection = field(default_factory=MockCollection)
    camera: Optional[MockObject] = None


class MockData:
    """Mock de bpy.data."""
    
    def __init__(self):
        self.objects: Dict[str, MockObject] = {}
        self.collections: Dict[str, MockCollection] = {}
        self.scenes: Dict[str, MockScene] = {"Scene": MockScene()}
        self.meshes: Dict[str, Any] = {}
        self.materials: Dict[str, Any] = {}
        self.images: Dict[str, Any] = {}
    
    def __getattr__(self, name: str):
        return {}


class MockContext:
    """Mock de bpy.context."""
    
    def __init__(self):
        self.scene = MockScene()
        self.view_layer = type('ViewLayer', (), {'objects': {'active': None}})()
        self.object = None
        self.selected_objects = []


class MockOps:
    """Mock de bpy.ops."""
    
    class wm:
        @staticmethod
        def save_as_mainfile(filepath: str = ""):
            return {'FINISHED'}
        
        @staticmethod
        def open_mainfile(filepath: str = ""):
            return {'FINISHED'}
    
    class object:
        @staticmethod
        def select_all(action: str = 'SELECT'):
            return {'FINISHED'}
        
        @staticmethod
        def delete():
            return {'FINISHED'}
        
        @staticmethod
        def modifier_add(type: str = 'SUBSURF'):
            return {'FINISHED'}
    
    class mesh:
        @staticmethod
        def primitive_cube_add(size: float = 1.0, location: Tuple = (0, 0, 0)):
            return {'FINISHED'}
        
        @staticmethod
        def primitive_plane_add(size: float = 1.0, location: Tuple = (0, 0, 0)):
            return {'FINISHED'}


class MockBpy:
    """Mock du module bpy."""
    
    data = MockData()
    context = MockContext()
    ops = MockOps()
    
    @staticmethod
    def app():
        return type('App', (), {'version': (4, 0, 0)})()


def patch_bpy():
    """
    Patch le module bpy avec le mock.
    
    Usage:
        from tests.mocks.mock_bpy import patch_bpy
        patch_bpy()
        import bpy  # Now uses MockBpy
    """
    import sys
    sys.modules['bpy'] = MockBpy
    sys.modules['mathutils'] = type('mathutils', (), {'Vector': MockVector})
    return MockBpy


def create_mock_scene() -> MockScene:
    """Crée une scène mock avec structure de base."""
    scene = MockScene(name="TestScene")
    
    room_shell = MockCollection(name="ROOM_SHELL")
    proxies = MockCollection(name="PROXIES")
    cameras = MockCollection(name="CAMERAS")
    
    scene.collection.children.append(room_shell)
    scene.collection.children.append(proxies)
    scene.collection.children.append(cameras)
    
    camera = MockObject(name="Camera", type="CAMERA")
    camera.location = MockVector(0, 0, 1.6)
    cameras.link(camera)
    scene.camera = camera
    
    return scene
