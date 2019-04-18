import bpy
from .. import uibase
from ..utils import *
from .smithy import engine_components
from .smithy.utils import *
import subprocess


class SmithyEngineComponentListAction(bpy.types.Operator, uibase.LexBaseListAction):
    bl_idname = "lexlistaction.smithy_engine_component_list_action"
    bl_label = "Smithy Engine-Component List Action"

    def get_collection(self):
        return bpy.context.object.lexgame.smithy.engine_components

    def get_index_property(self):
        return "active_engine_component_index"

    def get_index_source(self):
        return bpy.context.object.lexgame.smithy

    def on_add(self, item):
        item.init("health")


class SmithyScriptComponentListAction(bpy.types.Operator, uibase.LexBaseListAction):
    bl_idname = "lexlistaction.smithy_script_component_list_action"
    bl_label = "Smithy Script-Component List Action"

    def get_collection(self):
        return bpy.context.object.lexgame.smithy.script_components

    def get_index_property(self):
        return "active_script_component_index"

    def get_index_source(self):
        return bpy.context.object.lexgame.smithy

    def on_add(self, item):
        pass


class ComponentUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "filepath", text="", emboss=False)

    def invoke(self, context, event):
        i = "sup"


class LexGameScenePanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_lex_game_scene_panel"
    bl_label = "Smithy"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene

    def draw(self, context):
        layout = self.layout
        state_nodegroup = context.scene.lexsm.get_nodegroup()
        state = state_nodegroup.find_applied_state_node() if state_nodegroup else None
        if state:
            layout.label(text="State: " + state.lex_name)
            layout.operator('lexgame.edit_applied_smithy_state_script', text="Edit Script")
        else:
            layout.label(text="State: [None]")



class LexGameObjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lex_game_obj_panel"
    bl_label = "Smithy Components"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object and is_exportable(context.object)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        smithy_obj = obj.lexgame.smithy
        
        def draw_list_action(list_idname, action_col, action, icon):
            op = action_col.operator(list_idname, icon=icon, text="")
            op.action = action

        list_row = layout.row()
        list_row.template_list("ComponentUIList", "SmithyComponents",
                             smithy_obj, "script_components",
                             smithy_obj, "active_script_component_index",
                             rows=3)

        list_action_row = list_row.column(align=True)
        draw_list_action("lexlistaction.smithy_script_component_list_action", list_action_row, 'ADD', 'ADD')
        draw_list_action("lexlistaction.smithy_script_component_list_action", list_action_row, 'REMOVE', 'REMOVE')
        list_action_row.separator()

        if len(smithy_obj.script_components) > 1:
            draw_list_action("lexlistaction.smithy_script_component_list_action", list_action_row, 'UP', 'TRIA_UP')
            draw_list_action("lexlistaction.smithy_script_component_list_action", list_action_row, 'DOWN', 'TRIA_DOWN')

        if smithy_obj.active_script_component_index >= 0  and smithy_obj.active_script_component_index < len(smithy_obj.script_components):
            c = smithy_obj.script_components[smithy_obj.active_script_component_index]

            # component editing
            component_layout = layout.box() if len(c.inputs) > 0 else layout

            if c.file_exists:
                file_action_row = component_layout.row(align=True).split(factor=.25)
                file_action_row.operator("lexgame.open_smithy_component_script_external", text="Open")
            else:
                file_action_row = component_layout.row(align=True).split(factor=.3)
                file_action_row.operator("lexgame.new_smithy_component_script", icon="ADD", text="Create")

            # component properties
            if c.valid():
                for c_input in c.inputs:
                    c_input.draw(component_layout, context)
            else:
                component_layout.label(text=c.err_log)

        layout.separator()

        # if smithy_obj.active_engine_component_index >= 0:
        #     c = smithy_obj.engine_components[smithy_obj.active_engine_component_index]
        #     box = layout.box()

        #     # get component definition
        #     box.prop(c, 'component_type', text="")

        #     # component properties
        #     if c.valid():
        #         for p_item in c.fetch_properties():
        #             prop = p_item['bpy_property']
        #             prop_def = p_item['definition']
        #             prop.draw(prop_def, box)
        #     else:
        #         box.label("Invalid component name")

class OpenSmithyComponentScriptExternal(bpy.types.Operator):
    bl_idname = 'lexgame.open_smithy_component_script_external'
    bl_label = "Edit Smithy Component Script"
    
    @classmethod
    def poll(self, context):
        c_index = context.object.lexgame.smithy.active_script_component_index
        c = None
        if 0 <= c_index < len(context.object.lexgame.smithy.script_components):
            c = context.object.lexgame.smithy.script_components[c_index]
        return context.object and c and c.filepath != ""

    def execute(self, context):
        c_index = context.object.lexgame.smithy.active_script_component_index
        c = context.object.lexgame.smithy.script_components[c_index]
        
        script_filepath = abs_component_scriptpath(c.filepath)
        subprocess.run(['code', os.path.dirname(script_filepath), script_filepath], shell=True)

        return {"FINISHED"}


class NewSmithyComponentScript(bpy.types.Operator):
    bl_idname = 'lexgame.new_smithy_component_script'
    bl_label = "New Smithy Component Script"

    script_name : bpy.props.StringProperty(default="")

    @classmethod
    def poll(self, context):
        c_index = context.object.lexgame.smithy.active_script_component_index
        if 0 <= c_index < len(context.object.lexgame.smithy.script_components):
            c = context.object.lexgame.smithy.script_components[c_index]
        return context.object and c and c.filepath != ""

    def execute(self, context):
        def create_component_script(script_name):
            template_filepath = os.path.abspath(os.path.dirname(__file__) + "/templates/smithy_component_template.txt")
            with open(template_filepath, "r") as template_file:
                component_template = template_file.read()

            output_filepath = abs_component_scriptpath(script_name)
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            print("making", output_filepath)

            with open(output_filepath, "w") as script_file:
                component_name = os.path.basename(script_name)
                parsed_template = component_template.replace("${COMPONENT_NAME}", component_name)
                script_file.write(parsed_template)
            
            return script_name

        c_index = context.object.lexgame.smithy.active_script_component_index
        if c_index >= 0:
            c = context.object.lexgame.smithy.script_components[c_index]
            create_component_script(c.get_filepath())
            c.refresh()
            bpy.ops.lexgame.open_smithy_component_script_external()
        return {"FINISHED"}
