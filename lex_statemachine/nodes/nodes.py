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
        self.object_states.clear()

        objs = bpy.data.objects
        for o in objs:
            state = self.object_states.add()
            state.name = o.name
            state.save(o)
    
    def load_scene_state(self, scene):
        for state in self.object_states:
            obj = bpy.data.objects.get(state.name, None)
            if obj:
                state.load(obj)

    def set_lex_name_and_update(self, val):
        from .. import _scene_state_namechange_callbacks
        old_name = self.get('lex_name', self.name)
        for cb in _scene_state_namechange_callbacks:
            cb(self, old_name, val)
        self['lex_name'] = val

    def set_lex_name(self, val):
        self['lex_name'] = val

    def get_lex_name(self):
        return self.get('lex_name')

    lex_name : bpy.props.StringProperty(set=set_lex_name_and_update, get=get_lex_name)
    object_states : bpy.props.CollectionProperty(type=LexSM_ObjectState)
