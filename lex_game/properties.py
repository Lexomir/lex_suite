import bpy
from .. import handlers
from .smithy.properties import LexSmithyObject, LexSmithyScene
from .smithy import engine_components

class LexGameBase:
    prev_name : bpy.props.StringProperty(name="Previous Name")
    dirty : bpy.props.BoolProperty(name="Dirty")
    prev_dirty : bpy.props.BoolProperty(name="Previous Dirty")

class LexGameMaterial(bpy.types.PropertyGroup, LexGameBase):
    pass

class LexGameObject(bpy.types.PropertyGroup, LexGameBase):
    smithy : bpy.props.PointerProperty(type=LexSmithyObject)

class LexGameScene(bpy.types.PropertyGroup, LexGameBase):
    smithy : bpy.props.PointerProperty(type=LexSmithyScene)

class LexGameMesh(bpy.types.PropertyGroup, LexGameBase):
    pass

class LexGameLight(bpy.types.PropertyGroup, LexGameBase):
    pass

class LexGameCamera(bpy.types.PropertyGroup, LexGameBase):
    pass

class LexGameArmature(bpy.types.PropertyGroup, LexGameBase):
    pass

class LexGameTextCurve(bpy.types.PropertyGroup, LexGameBase):
    pass
 
class LexGameMaterialPanel(bpy.types.Panel):
    bl_idname = "Game_Material_panel"
    bl_label = "Game"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        if context.object.active_material:
            mat = context.object.active_material
            self.layout.prop(mat.lexgame, 'dirty')


def register():
    bpy.types.Material.lexgame = bpy.props.PointerProperty(type=LexGameMaterial)
    bpy.types.Object.lexgame = bpy.props.PointerProperty(type=LexGameObject)
    bpy.types.Scene.lexgame = bpy.props.PointerProperty(type=LexGameScene)
    bpy.types.Mesh.lexgame = bpy.props.PointerProperty(type=LexGameMesh)
    bpy.types.Camera.lexgame = bpy.props.PointerProperty(type=LexGameCamera)
    bpy.types.Light.lexgame = bpy.props.PointerProperty(type=LexGameLight)
    bpy.types.Armature.lexgame = bpy.props.PointerProperty(type=LexGameArmature)
    bpy.types.TextCurve.lexgame = bpy.props.PointerProperty(type=LexGameTextCurve)

def unregister():
    del bpy.types.Material.lexgame
    del bpy.types.Object.lexgame
    del bpy.types.Mesh.lexgame
    del bpy.types.Camera.lexgame
    del bpy.types.Light.lexgame
    del bpy.types.Armature.lexgame