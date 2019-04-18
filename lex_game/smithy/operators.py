import bpy
import os
import subprocess
from .utils import abs_state_scriptpath

def create_state_script(output_filepath):
    template_filepath = os.path.normpath(os.path.abspath(os.path.dirname(__file__) + "/../templates/smithy_state_script_template.txt"))
    with open(template_filepath, "r") as template_file:
        script_template = template_file.read()

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    print("Making State Script: ", output_filepath)

    with open(output_filepath, "w") as script_file:
        script_file.write(script_template)

    return output_filepath


class LexSmithy_EditAppliedStateScript(bpy.types.Operator):
    bl_idname = 'lexgame.edit_applied_smithy_state_script'
    bl_label = "LexGame Smithy Edit Applied State Script"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        # get state name, find lua file
        state_nodegroup = context.scene.lexsm.get_nodegroup()
        state = state_nodegroup.find_applied_state_node() if state_nodegroup else None
        
        if not state:
            return {"CANCELED"}
        
        script_filepath = abs_state_scriptpath(state.name)
        if not os.path.exists(script_filepath):
            create_state_script(script_filepath)

        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}

class LexSmithy_EditSelectedStateScript(bpy.types.Operator):
    bl_idname = 'lexgame.edit_selected_smithy_state_script'
    bl_label = "LexGame Smithy Edit Selected State Script"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        # get state name, find lua file
        state_nodegroup = context.scene.lexsm.get_nodegroup()
        state = state_nodegroup.nodes.active if state_nodegroup else None
        
        if not state:
            return {"CANCELED"}
        
        script_filepath = abs_state_scriptpath(state.name)
        if not os.path.exists(script_filepath):
            create_state_script(script_filepath)

        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}
