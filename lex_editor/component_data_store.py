import bpy
from types import SimpleNamespace, MethodType

_objects_cache = {}

class ComponentInstance:
    def __init__(self, bpy_object, functions):
        self.object = bpy_object

        for name, func in functions.items():
            setattr(self, name, MethodType(func, self))
    
    def create_mesh_object(self, name):
        actual_name = "{}_LX_GENERATED".format(name)
        mesh = bpy.data.meshes.get(actual_name)
        if not mesh:
            mesh = bpy.data.meshes.new(actual_name)

        obj = bpy.data.objects.get(actual_name)
        if not obj:
            obj = bpy.data.objects.new(actual_name, mesh)
            bpy.context.scene.objects.link(obj)
            
        obj.parent = self.object
        return obj
            



def get_or_create_component_instance(obj, component):
    obj_data = _objects_cache.setdefault(obj.name, {})
    component_instance = obj_data.setdefault(component.filepath, ComponentInstance(bpy_object=obj))
    return component_instance

def get_component_instance(obj, component):
    return _objects_cache.get(obj.name, {}).get(component.filepath, None)


def create_component_instance(obj, component):
    obj_data = _objects_cache.setdefault(obj.name, {})
    component_instance = ComponentInstance(bpy_object=obj, functions=component.script_functions)
    obj_data[component.filepath] = component_instance
    return component_instance
