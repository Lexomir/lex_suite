import bpy
from ..utils import *
from . import unity_context
from .. import handlers
from .types import Mesh, Skeleton


def export_material(material):
    if material.node_tree:
        nodes = material.node_tree.nodes
        output_node = get_active_output_node(nodes)
        shader_socket = output_node.inputs['Surface']

        if len(shader_socket.links) != 1:
            print("Material has no shader connected to the output")
            return

        shader_node = shader_socket.links[0].from_node
        unity_context.export_material(material, shader_node, bpy.context.scene)

def export_object(obj, scene):
    unity_context.export_object(obj, scene)

def export_model(mesh_obj, scene):
    armature = get_affecting_armature(mesh_obj)
    skeleton = None
    if armature:
        skeleton = Skeleton(armature)

    mesh = Mesh(mesh_obj, skeleton)

    unity_context.export_mesh(mesh_obj, mesh, skeleton, scene)

def export_scene(scene):
    unity_context.export_scene(scene)

    # broadcast changes 
    if hasattr(bpy.types, "EXTERNAL_OT_broadcast_load_scene"):
        bpy.ops.external.broadcast_load_scene()


#------------------------------------------------------
def set_active_output_node(my_node):
    nodes = my_node.id_data.nodes
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            node.is_active_output = False
    my_node.is_active_output = True


def get_active_output_node(nodes):
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
            return node
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            return node


class ExportSelectedObjectMaterial(bpy.types.Operator):
    bl_idname = "export.export_selected_object_material"
    bl_label = "Export Selected Object Material"
    
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        print("Exporting Materials")

        exportable_materials = [obj.active_material for obj in context.selected_objects if obj.active_material]
        for mat in exportable_materials:
            export_material(mat)
    
        return {"FINISHED"}

# callback when the save completes
do_after_save = None

# clear the dirty bits (they will be exported after the save finishes)
def _on_file_saved_pre(dummy):
    exportable_materials = [mat for mat in bpy.data.materials if mat.lexgame.dirty]
    for mat in exportable_materials:
        mat.lexgame.dirty = False

    exportable_objects = [obj for obj in bpy.data.objects if obj.lexgame.dirty]
    for obj in exportable_objects:
        obj.lexgame.dirty = False

    exportable_meshes = [obj for obj in bpy.data.objects if is_exportable_mesh_object(obj) and obj.data.lexgame.dirty]
    for mesh_obj in exportable_meshes:
        mesh_obj.data.lexgame.dirty = False

    def export_them_all():
        for mat in exportable_materials:
            export_material(mat)
        for obj in exportable_objects:
            export_object(obj, bpy.context.scene)
        for mesh_obj in exportable_meshes:
            export_model(mesh_obj, bpy.context.scene)
        export_scene(bpy.context.scene)
    
    global do_after_save
    do_after_save = export_them_all


def _on_file_save_post(dummy):
    global do_after_save
    if do_after_save:
        do_after_save()

