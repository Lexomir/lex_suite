import bpy
from ..utils import refresh_screen_area
from .nodes.node_trees import LexSM_BaseNodeTree

class LexSM_SaveObjectState(bpy.types.Operator):
    bl_idname = 'lexsm.save_object_state'
    bl_label = "LexSM Save Object State"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        obj = context.object

        applied_state_node = obj.lexsm.get_nodegroup().find_applied_state()
        if applied_state_node:
            applied_state_node.save_object_state(obj)
            
            refresh_screen_area("PROPERTIES")

        return {"FINISHED"}

class LexSM_LoadObjectState(bpy.types.Operator):
    bl_idname = 'lexsm.load_object_state'
    bl_label = "LexSM Load Object State"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        obj = context.object

        applied_state_node = obj.lexsm.get_nodegroup().find_applied_state()
        if applied_state_node:
            applied_state_node.load_object_state(obj)

            refresh_screen_area("PROPERTIES")
            
        return {"FINISHED"}


class LexSM_ApplySelectedStateNode(bpy.types.Operator):
    bl_idname = 'lexsm.apply_selected_state_node'
    bl_label = "LexSM Apply Selected State Node"

    @classmethod
    def poll(cls, context):
        node_group = context.space_data.node_tree
        return context.area.type == "NODE_EDITOR" and isinstance(node_group, LexSM_BaseNodeTree)
    
    def execute(self, context):
        node_group = context.space_data.node_tree
        if node_group and isinstance(node_group, LexSM_BaseNodeTree):
            print("applying state")
            node_group.apply_active_state()

        refresh_screen_area("PROPERTIES")

        return {"FINISHED"}

class LexSM_ApplyStateNodeUnderCursor(bpy.types.Operator):
    bl_idname = 'lexsm.apply_state_node_under_cursor'
    bl_label = "LexSM Apply State Node Under Cursor"

    @classmethod
    def poll(cls, context):
        node_group = context.space_data.node_tree
        return context.area.type == "NODE_EDITOR" and isinstance(node_group, LexSM_BaseNodeTree)
    
    def invoke(self, context, event):
        node_group = context.space_data.node_tree

        bpy.ops.node.select(mouse_x=event.mouse_region_x, mouse_y=event.mouse_region_y, extend=False)
        bpy.ops.lexsm.apply_selected_state_node()

        return {"FINISHED"}

class LexSM_ContextChecker(bpy.types.Operator):
    bl_idname = 'lexsm.context_checker'
    bl_label = "LexSM Print Context space info"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print(context.space_data.node_tree)

        return {"FINISHED"}
