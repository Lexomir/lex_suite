import bpy
from .. import uibase
from ..utils import *

class LexSM_ObjectStateListAction(bpy.types.Operator, uibase.LexBaseListAction):
    bl_idname = "lexlistaction.lexsm_object_state_list_action"
    bl_label = "Lex SM Object State List Action"

    def get_collection(self):
        return bpy.context.object.lexsm.states

    def get_index_property(self):
        return "active_state_index"

    def get_index_source(self):
        return bpy.context.object.lexsm

    def on_add(self, item):
        pass


class LexSM_ObjectStateUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.get_name())

    def invoke(self, context, event):
        pass


class LexSM_ObjectStatePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lexsm_obj_state_panel"
    bl_label = "State Machine"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        obj = context.object
        sm = obj.lexsm

        layout.prop_search(sm, "node_group", bpy.data, "node_groups", text="", text_ctxt="", translate=True, icon='NONE')

        node_group = sm.get_nodegroup()
        if node_group:
            applied_state = node_group.find_applied_state_node()
            if applied_state:
                input_states = applied_state.get_input_states()
                output_states = applied_state.get_output_states()
                for state in output_states:
                    # layout.operator("switch_to_object_state")
                    pass

class LexSM_SceneStatePanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_lexsm_scene_state_panel"
    bl_label = "State Machine"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sm = scene.lexsm

        layout.prop_search(sm, "node_group", bpy.data, "node_groups", text="", text_ctxt="", translate=True, icon='NONE')

        node_group = sm.get_nodegroup()
        if node_group:
            applied_state = node_group.find_applied_state_node()
            if applied_state:
                input_states = applied_state.get_input_states()
                output_states = applied_state.get_output_states()
                for state in output_states:
                    # layout.operator("switch_to_object_state")
                    pass

