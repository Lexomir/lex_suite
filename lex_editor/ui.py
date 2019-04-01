import bpy
from .. import uibase
from ..utils import *
from .utils import abs_editor_scriptpath
from . import editor
import subprocess

class LexEditorComponentPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lex_editor_component_panel"
    bl_label = "Editor Components"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        def draw_list_action(list_idname, action_col, action, icon):
            op = action_col.operator(list_idname, icon=icon, text="")
            op.action = action

        list_row = layout.row()
        list_row.template_list("EditorComponentUIList", "EditorComponents",
                             obj.lexeditor, "components",
                             obj.lexeditor, "active_component_index",
                             rows=3)

        list_action_row = list_row.column(align=True)
        draw_list_action("lexlistaction.editor_component_list_action", list_action_row, 'ADD', 'ADD')
        draw_list_action("lexlistaction.editor_component_list_action", list_action_row, 'REMOVE', 'REMOVE')

        list_action_row.separator()

        if len(obj.lexeditor.components) > 1:
            draw_list_action("lexlistaction.editor_component_list_action", list_action_row, 'UP', 'TRIA_UP')
            draw_list_action("lexlistaction.editor_component_list_action", list_action_row, 'DOWN', 'TRIA_DOWN')

        if obj.lexeditor.active_component_index >= 0 and obj.lexeditor.active_component_index < len(obj.lexeditor.components):
            c = obj.lexeditor.components[obj.lexeditor.active_component_index]

            # component editing
            component_layout = layout.box() if len(c.inputs) > 0 else layout

            if c.file_exists:
                file_action_row = component_layout.row(align=True).split(factor=.25)
                file_action_row.operator("lexeditor.open_editor_component_script_external", text="Edit")
            else:
                file_action_row = component_layout.row(align=True).split(factor=.3)
                file_action_row.operator("lexeditor.new_editor_component_script", text="Create")

            # component properties
            if c.valid():
                for c_input in c.inputs:
                    c_input.draw(component_layout, context)
            else:
                component_layout.label(text=c.err_log)

        layout.separator()
            


class EditorComponentUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "filepath", text="", emboss=False)

    def invoke(self, context, event):
        pass

class EditorComponentListAction(bpy.types.Operator, uibase.LexBaseListAction):
    bl_idname = "lexlistaction.editor_component_list_action"
    bl_label = "Editor Component List Action"

    def get_collection(self):
        return bpy.context.object.lexeditor.components

    def get_index_property(self):
        return "active_component_index"

    def get_index_source(self):
        return bpy.context.object.lexeditor

    def on_add(self, item):
        pass

    def on_remove(self, item):
        editor.stop_component(item)


class OpenEditorComponentScriptExternal(bpy.types.Operator):
    bl_idname = 'lexeditor.open_editor_component_script_external'
    bl_label = "Edit Editor Component Script"
    
    @classmethod
    def poll(self, context):
        c_index = context.object.lexeditor.active_component_index
        if c_index >= 0:
            c = context.object.lexeditor.components[c_index]
        return context.object and c_index >= 0 and c.filepath != ""

    def execute(self, context):
        c_index = context.object.lexeditor.active_component_index
        c = context.object.lexeditor.components[c_index]
        
        script_filepath = abs_editor_scriptpath(c.filepath)
        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}


class NewEditorComponentScript(bpy.types.Operator):
    bl_idname = 'lexeditor.new_editor_component_script'
    bl_label = "New Editor Component Script"

    script_name : bpy.props.StringProperty(default="")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        def create_component_script(script_name):
            template_filepath = os.path.abspath(os.path.dirname(__file__) + "/templates/bpy_component_template.txt")
            with open(template_filepath, "r") as template_file:
                component_template = template_file.read()

            script_basename = script_name
            output_filepath = abs_editor_scriptpath(script_basename)
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            print("making", output_filepath)

            with open(output_filepath, "w") as script_file:
                script_file.write(component_template)
            
            return script_basename

        c_index = context.object.lexeditor.active_component_index
        if c_index >= 0:
            c = context.object.lexeditor.components[c_index]
            create_component_script(c.get_filepath())
            c.refresh()
            bpy.ops.lexeditor.open_editor_component_script_external()
        return {"FINISHED"}

class RefreshEditorComponentScript(bpy.types.Operator):
    bl_idname = 'lexeditor.refresh_editor_component_script'
    bl_label = "Refresh Editor Componentt Script"

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        c_index = context.object.lexeditor.active_component_index
        if c_index >= 0:
            c = context.object.lexeditor.components[c_index]
            editor.compile_component(c)
            editor.start_component(c)
        return {"FINISHED"}

