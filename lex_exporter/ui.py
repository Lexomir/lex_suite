import bpy
from bpy.types import Menu

class VIEW3D_PIE_lex_export(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("export.export_objects_as_moe")
        pie.operator("export.export_all_actions_as_mad")


class LexExportActionPropertyGroup(bpy.types.PropertyGroup):
    is_looping : bpy.props.BoolProperty(default=True)

class ACTIONEDITOR_PT_lex_action(bpy.types.Panel):
    # label is displayed at the center of the pie menu.
    bl_label = "Lex Action"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return context.object and context.object.animation_data
        
    def draw(self, context):
        layout = self.layout
        bl_action = context.object.animation_data.action
        layout.prop(bl_action.lex_export, "is_looping")


def register():
    bpy.types.Action.lex_export = bpy.props.PointerProperty(type=LexExportActionPropertyGroup)

def unregister():
    del bpy.types.Action.lex_export
