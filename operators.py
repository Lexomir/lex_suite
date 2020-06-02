import bpy


class VIEW3D_PIE_lex_object_mode(bpy.types.Menu):
    """Object Mode (Pie Menu)"""
    bl_label = "Object Mode (Pie Menu)"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        def create_mode_set_operator(pie, mode):
            op = pie.operator("object.mode_set", text=mode)
            op.mode = mode
            op.toggle=False
            return op

        layout = self.layout
        pie = layout.menu_pie()
        if context.object.type == "MESH":
            create_mode_set_operator(pie, "OBJECT")
            create_mode_set_operator(pie, "EDIT")
            create_mode_set_operator(pie, "SCULPT")
            create_mode_set_operator(pie, "WEIGHT_PAINT")
            create_mode_set_operator(pie, "TEXTURE_PAINT")
            create_mode_set_operator(pie, "VERTEX_PAINT")
        elif context.object.type == "ARMATURE":
            create_mode_set_operator(pie, "OBJECT")
            create_mode_set_operator(pie, "EDIT")
            create_mode_set_operator(pie, "POSE")
