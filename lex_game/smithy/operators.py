import bpy
import os
import subprocess
from .utils import abs_state_scriptpath


class LexSmithy_EditAppliedStateScript(bpy.types.Operator):
    bl_idname = 'lexgame.edit_applied_smithy_state_script'
    bl_label = "LexGame Smithy Edit Applied State Script"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Save the project first. This operation needs a project folder.")
            return {"CANCELLED"}

        # get state name, find lua file
        state_nodegroup = context.scene.lexsm.get_nodegroup()
        state = state_nodegroup.find_applied_state_node() if state_nodegroup else None
        
        if not state:
            return {"CANCELLED"}

        if not state_script_exists(state.name):
            create_state_script(state.name)

        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}

class LexSmithy_EditSelectedStateScript(bpy.types.Operator):
    bl_idname = 'lexgame.edit_selected_smithy_state_script'
    bl_label = "LexGame Smithy Edit Selected State Script"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Save the project first. This operation needs a project folder.")
            return {"CANCELLED"}

        # get state name, find lua file
        state_nodegroup = context.scene.lexsm.get_nodegroup()
        state = state_nodegroup.nodes.active if state_nodegroup else None
        
        if not state:
            return {"CANCELLED"}
        
        script_filepath = abs_state_scriptpath(state.name)
        if not os.path.exists(script_filepath):
            create_state_script(script_filepath)

        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}
