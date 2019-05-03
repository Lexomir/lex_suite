import bpy
from .utils import *
from ...generic_value import GenericValue

__reload_order_index__ = -1  # register before smithy.properties.register


class LexSmithyScriptComponentInput(bpy.types.PropertyGroup, GenericValue):
    pass

class LexSmithyScriptComponent(bpy.types.PropertyGroup):
    def set_filepath(self, filepath):
        self['filepath'] = filepath

    def get_filepath(self):
        return self['filepath'] if 'filepath' in self else ""            
    
    filepath : bpy.props.StringProperty(default="", set=set_filepath, get=get_filepath)
    inputs : bpy.props.CollectionProperty(type=LexSmithyScriptComponentInput)
    file_exists : bpy.props.BoolProperty(default=False)
    err_log : bpy.props.StringProperty(default="")

class LexSmithyObject(bpy.types.PropertyGroup):
    active_script_component_index : bpy.props.IntProperty(default=-1)
    script_components : bpy.props.CollectionProperty(type=LexSmithyScriptComponent)

class LexSmithyScene(bpy.types.PropertyGroup):
    pass


def register():
    return

def unregister():
    pass