import bpy
from ..properties import LexStringProperty

from .. import lex_editor

__reload_order_index__ = -2


class LexSM_SerializedComponent(bpy.types.PropertyGroup):
    filepath : bpy.props.StringProperty()
    data : bpy.props.StringProperty()


class LexSM_ObjectState(bpy.types.PropertyGroup):
    smithy_components_serialized : bpy.props.CollectionProperty(type=LexSM_SerializedComponent)
    editor_components_serialized : bpy.props.CollectionProperty(type=LexSM_SerializedComponent)
    custom_state_data : bpy.props.CollectionProperty(type=LexStringProperty)
    location : bpy.props.FloatVectorProperty(size=3)
    scale : bpy.props.FloatVectorProperty(size=3)
    dimensions : bpy.props.FloatVectorProperty(size=3)
    rotation_quaternion : bpy.props.FloatVectorProperty(size=4)


class LexSM_Object(bpy.types.PropertyGroup):
    node_group : bpy.props.StringProperty()


class LexSM_Scene(bpy.types.PropertyGroup):
    node_group : bpy.props.StringProperty()


def register():
    bpy.types.Object.lexsm = bpy.props.PointerProperty(type=LexSM_Object)
    bpy.types.Scene.lexsm = bpy.props.PointerProperty(type=LexSM_Scene)

def unregister():
    del bpy.types.Object.lexsm
    del bpy.types.Scene.lexsm
