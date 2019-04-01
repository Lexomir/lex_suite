import bpy

__reload_order_index__ = -10

class LexStringProperty(bpy.types.PropertyGroup):
    value : bpy.props.StringProperty()


class LexTagProperty(bpy.types.PropertyGroup):
    pass