import sys
from ..utils import *
from mathutils import Matrix
from math import radians
from ..lexmath import Vec3
from . import unity_shader_exporter, moe_exporter
from os.path import basename, splitext


# (x, y, z) --> (-x, z, -y)
_mirror_x = Matrix([
    [-1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]])
_blender_to_unity_space = Matrix.Rotation(radians(-90), 4, "X") @ _mirror_x
_self = sys.modules[__name__]


options = ExportOptions.MATRIX_IBP


# Exports

def export_mesh(mesh_obj, mesh, skeleton, scene):
    # export moe (pass _self as context)
    filepath = moe_abs_filepath_of_mesh(mesh_obj.data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    moe_exporter.export_moe(mesh, skeleton, filepath, _self)
    pass

def export_object(obj, scene):
    # export gob (pass _self as context)
    pass

def export_scene(scene):
    # export scene (pass _self as context)
    # scene_filename = splitext(basename(bpy.data.filepath))[0]
    # scene_filepath = bpy.path.abspath("//") + "Scenes/" + scene_filename + ".scene"
    #os.makedirs(os.path.dirname(scene_filepath), exist_ok=True)

    #scene_exporter.export_scene(scene_filepath, scene, _self)
    pass

def export_material(material, shader_node, scene):
    # export shader
    # filepath = bpy.path.abspath("//") + "Assets/Shaders/" + make_valid_name(material.name) + ".shader"
    # os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # unity_shader_exporter.export_shader(material, shader_node, filepath)
    # export material definition
    pass


# Filepaths

def moe_local_filepath_of_mesh(mesh):
    return "Export/" + mesh.name + ".moe"

def mad_local_filepath_of_anim(anim):
    return "Export/" + anim.name + ".mad"

def _get_abs_path(assetPath):
    return bpy.path.abspath("//") + assetPath

def moe_abs_filepath_of_mesh(mesh):
    return _get_abs_path(moe_local_filepath_of_mesh(mesh))

def mad_abs_filepath_of_anim(anim):
    return _get_abs_path(mad_local_filepath_of_anim(anim))

# GameObject Transforms

def get_object_matrix_local(obj):
    # calculate the 'actual' local matrix (since the parent isn't necessarily the object blender thinks it is)
    parent = find_exportable_parent(obj)
    local_matrix = obj.matrix_world
    if parent:
        local_matrix = parent.matrix_world.inverted() @ obj.matrix_world

    # convert to unity axis
    local_matrix = convert_matrix(local_matrix)

    if obj.type == "CAMERA":
        camera_orientation_offset = Matrix.Rotation(radians(90), 4, "X") @ Matrix.Rotation(radians(180), 4, "Z")
        return local_matrix @ camera_orientation_offset
    if obj.type == "LIGHT":
        light_orientation_offset = Matrix.Rotation(radians(90), 4, "X")
        return local_matrix @ light_orientation_offset

    return local_matrix


# Realigning Coordinates

# (x, y, z) --> (-x, z, -y)
def convert_matrix(matrix):
    return _blender_to_unity_space @ matrix @ _blender_to_unity_space.inverted()

def convert_vector(vec):
    return (-vec[0], vec[2], -vec[1])
