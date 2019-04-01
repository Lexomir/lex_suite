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

    object_states : bpy.props.CollectionProperty(type=LexSM_ObjectState)
