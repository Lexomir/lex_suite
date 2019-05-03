import bpy
from .base import LexSM_BaseStateNode
from ..properties import LexSM_ObjectState

__reload_order_index__ = -1



class LexSM_ObjectStateNode(bpy.types.Node, LexSM_BaseStateNode):
    bl_idname = "LexSM_ObjectStateNode"
    bl_label = "State"
    bl_icon = 'NONE'

    object_state : bpy.props.PointerProperty(type=LexSM_ObjectState)


class LexSM_SceneStateNode(bpy.types.Node, LexSM_BaseStateNode):
    bl_idname = "LexSM_SceneStateNode"
    bl_label = "State"
    bl_icon = 'NONE'

    def save_scene_state(self, scene):
        assert False

    
    def load_scene_state(self, scene):
        assert False

    
    def set_lex_name(self, val):
        self['lex_name'] = val

    def get_lex_name(self):
        return self.get('lex_name')

    lex_name : bpy.props.StringProperty(set=set_lex_name, get=get_lex_name)
    object_states : bpy.props.CollectionProperty(type=LexSM_ObjectState)
