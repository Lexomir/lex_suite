import bpy
from ..utils import *
from . import moe_exporter
from . import config, unity_context
from .types import Mesh, Skeleton


class MoeExportSelectedObjects(bpy.types.Operator):
    bl_idname = "export.export_objects_as_moe"
    bl_label = "Moe Export (Selected Objects)"
    bl_description = "Exports all selected meshes as Moe"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == "MESH":
                return True
        return False

    def invoke(self, context, event):
        print("Exporting Moes")
        
        moe_exporter.export_mesh_objects_as_moe(context.selected_objects, unity_context)

        return {"FINISHED"}
