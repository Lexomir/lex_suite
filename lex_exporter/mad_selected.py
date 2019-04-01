import bpy
from .. import utils
from . import mad_exporter, config, unity_context
from .types import Skeleton, Animation


class MadExportActiveAction(bpy.types.Operator):
    bl_idname = "export.export_active_action_as_mad"
    bl_label = "Mad Export (Active Action Only)"
    bl_description = "Exports the active action associated with the active armature"
    
    @classmethod
    def poll(cls, context):
        has_armature = utils.get_affecting_armature(context.object) is not None
        is_armature = context.object is not None and context.object.type == "ARMATURE"
        return is_armature or has_armature
    
    def invoke(self, context, event):        
        object = context.object
        if object is None:
            return {"CANCELLED"}
            
        is_armature = context.object.type == "ARMATURE"
        armature = context.object if is_armature else utils.get_affecting_armature(context.object)

        skeleton = Skeleton(armature)

        if armature.animation_data:        
            export_action_as_mad(armature.animation_data.action)
        
        return {"FINISHED"}

class MadExportAllAction(bpy.types.Operator):
    bl_idname = "export.export_all_actions_as_mad"
    bl_label = "Mad Export (All Actions)"
    bl_description = "Exports all actions (plays them through the active armature)"
    
    @classmethod
    def poll(cls, context):
        has_armature = utils.get_affecting_armature(context.object) is not None
        is_armature = context.object is not None and context.object.type == "ARMATURE"
        return is_armature or has_armature
    
    def invoke(self, context, event):        
        object = context.object
        if object is None:
            return {"CANCELLED"}
            
        is_armature = context.object.type == "ARMATURE"
        armature = context.object if is_armature else utils.get_affecting_armature(context.object)

        skeleton = Skeleton(armature)

        for bl_action in bpy.data.actions:     
            export_action_as_mad(bl_action, armature, skeleton)
        
        return {"FINISHED"}


def export_action_as_mad(bl_action, armature, skeleton):
    animation_name = bl_action.name
    animation = Animation(animation_name, armature, bl_action, skeleton)
    filepath = unity_context.mad_abs_filepath_of_anim(animation)
    mad_exporter.export_mad(animation, skeleton, filepath, export_context=unity_context)
            