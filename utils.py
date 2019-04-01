import bpy
import importlib
import os
from mathutils import Vector, Matrix
import math

class ExportOptions:
    NONE = 0
    MATRIX_IBP = 1
    UNITY_COORDINATES = 2
    EULER_MATRIX = 4   # matrix rotations will be in euler form rather than quaternion form


def get_blend_filename():
    blend_filepath = bpy.data.filepath
    assert blend_filepath != ""
    filename_with_extention = bpy.path.basename(blend_filepath)
    return os.path.splitext(filename_with_extention)[0]

def refresh_screen_area(area_type):
    for area in bpy.context.screen.areas:
        if area.type == area_type:
            area.tag_redraw()

def get_project_dir():
    return bpy.path.abspath("//")

def make_valid_name(old_name):
    return old_name #old_name.replace(".", "_").replace(" ", "_")

def make_valid_bone_name(old_name):
    return old_name #old_name.upper().replace(".", "_")

def serialize_quat_transform_without_scale(matrix):
    pos, quat, scale = matrix.decompose()
    quat.normalize()
    return "{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}".format(quat.w, quat.x, quat.y, quat.z, pos.x, pos.y, pos.z)

def serialize_quat_transform(matrix, with_parentheses=False):
    pos, quat, scale = matrix.decompose()
    quat.normalize()
    return serialize_quat_from_decomposed(pos, quat, scale, with_parentheses=with_parentheses)

def serialize_quat_from_decomposed(pos, quat, scale, with_parentheses=False):
    quat.normalize()
    if with_parentheses:
        return "({:.3f}\t{:.3f}\t{:.3f}\t{:.3f})\t({:.3f}\t{:.3f}\t{:.3f})\t({:.3f}\t{:.3f}\t{:.3f})".format(quat.w, quat.x, quat.y, quat.z, pos.x, pos.y, pos.z, scale.x, scale.y, scale.z)
    else:
        return "{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}".format(quat.w, quat.x, quat.y, quat.z, pos.x, pos.y, pos.z, scale.x, scale.y, scale.z)
    
def serialize_euler_transform(matrix):
    pos = matrix.translation
    rot = matrix.to_euler()
    scale = matrix.to_scale()
    return "{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}".format(rot.x, rot.y, rot.z, pos.x, pos.y, pos.z, scale.x, scale.y, scale.z)

def serialize_matrix_transform(matrix):
    serialized = ""
    for col in matrix.col:
        serialized += "{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t".format(col.x, col.y, col.z, col.w)
    return serialized[:-1] # remove trailing space


def normalize_weights(weights):
    total_weight = 0
    # get three hights weights
    sorted_weights = sorted(weights, key=lambda x: x[1])[-3:]
    for weight in sorted_weights:
        bone_id, weight_value = weight
        total_weight = total_weight + weight_value
        
    normalized_weights = []
    for weight in sorted_weights:
        bone_id, weight_value = weight
        normalized_weight = weight_value / total_weight if total_weight > 0 else 0
        normalized_weights.append((bone_id, normalized_weight))

    # insanity check that there are three weights that add to 1
    total = 0
    assert len(normalized_weights) <= 3
    used_bones = []
    for weight in normalized_weights:
        bone_id, weight_value = weight
        # if bone_id in used_bones:
        #     print("troublesome weights:")
        #     print(weights)
        # assert bone_id not in used_bones
        used_bones.append(bone_id)
        total += weight_value
    assert .9 < total < 1.1 or total == 0

    return normalized_weights

        
def get_unique_mesh_objects(objects):
    unique_meshes = []
    unique_mesh_objects = []
    for obj in objects:
        if obj.type == "MESH":
            if not is_externally_linked(obj.data):
                most_suitable_object = get_most_suitable_object(obj.data)
                if obj.data not in unique_meshes:
                    unique_meshes.append(obj.data)
                    unique_mesh_objects.append(most_suitable_object)
    return unique_mesh_objects
    

def get_affecting_armature(obj):
    if obj is not None and obj.parent is not None and obj.parent.type == 'ARMATURE':
        proxy_obj = find_proxy(obj.parent)
        return proxy_obj if proxy_obj else obj.parent
    else:
        return None
        
        
def find_proxy(obj):
    for other_obj in bpy.data.objects:
        if other_obj.type == 'ARMATURE' or other_obj.type == 'MESH':
            if other_obj.proxy == obj:
                return other_obj
                

# get an object that contains a given mesh
# object with armature has priority
def get_most_suitable_object(mesh):
    most_suitable = {}
    for obj in bpy.data.objects:
        if obj.data == mesh:
            if get_affecting_armature(obj) is not None:
                return obj
            most_suitable = obj
    return most_suitable


def count_ancestors(obj):
    if obj.parent:
        return 1 + count_ancestors(obj.parent)
    else:
        return 0

def is_externally_linked(data):
    return data.library is not None


def gob_filepath_local(obj):
    return "GameObjects/{}.gob".format(make_valid_name(obj.name))

def gob_filepath_absolute(obj):
    return bpy.path.abspath("//") + gob_filepath_local(obj)

def is_exportable(obj):
    return obj.type != 'ARMATURE' and not obj.hide_viewport and not is_tmp_object(obj)

def find_exportable_parent(obj):
    parent = obj.parent
    if parent != None:
        if is_exportable(parent):
            return parent
        else:
            return find_exportable_parent(parent)
    else:
        return None

def get_scene_name(scene):
    return os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0]

tmp_object_suffix = "_LEX_ADDON_TEMP_OBJ_XDXDXDXD"

def create_tmp_object(name, data):
    return bpy.data.objects.new(name=name + tmp_object_suffix, object_data=data)

def is_tmp_object(obj):
    global tmp_object_suffix
    return obj.name[-len(tmp_object_suffix):] == tmp_object_suffix

def is_exportable_mesh_object(mesh_obj):
    return (mesh_obj.type == "MESH" 
        and mesh_obj.data 
        and len(mesh_obj.data.vertices) >= 3)
        

def vec_roll_to_mat3(vec, roll):
    #port of the updated C function from armature.c
    #https://developer.blender.org/T39470
    #note that C accesses columns first, so all matrix indices are swapped compared to the C version

    nor = vec.normalized()
    THETA_THRESHOLD_NEGY = 1.0e-9
    THETA_THRESHOLD_NEGY_CLOSE = 1.0e-5

    #create a 3x3 matrix
    bMatrix = Matrix().to_3x3()

    theta = 1.0 + nor[1]

    if (theta > THETA_THRESHOLD_NEGY_CLOSE) or ((nor[0] or nor[2]) and theta > THETA_THRESHOLD_NEGY):

        bMatrix[1][0] = -nor[0]
        bMatrix[0][1] = nor[0]
        bMatrix[1][1] = nor[1]
        bMatrix[2][1] = nor[2]
        bMatrix[1][2] = -nor[2]
        if theta > THETA_THRESHOLD_NEGY_CLOSE:
            #If nor is far enough from -Y, apply the general case.
            bMatrix[0][0] = 1 - nor[0] * nor[0] / theta
            bMatrix[2][2] = 1 - nor[2] * nor[2] / theta
            bMatrix[0][2] = bMatrix[2][0] = -nor[0] * nor[2] / theta

        else:
            #If nor is too close to -Y, apply the special case.
            theta = nor[0] * nor[0] + nor[2] * nor[2]
            bMatrix[0][0] = (nor[0] + nor[2]) * (nor[0] - nor[2]) / -theta
            bMatrix[2][2] = -bMatrix[0][0]
            bMatrix[0][2] = bMatrix[2][0] = 2.0 * nor[0] * nor[2] / theta

    else:
        #If nor is -Y, simple symmetry by Z axis.
        bMatrix = Matrix().to_3x3()
        bMatrix[0][0] = bMatrix[1][1] = -1.0

    #Make Roll matrix
    rMatrix = Matrix.Rotation(roll, 3, nor)

    #Combine and output result
    mat = rMatrix * bMatrix
    return mat

def mat3_to_vec_roll(mat):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv * mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return vec, roll