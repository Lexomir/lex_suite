import mathutils
import bpy
import bmesh
from ..lexmath import Vec3, Vec2
from ..utils import *
from ..collection_extras import OrderedSet

    

def output_matrix(matrix):
    pos, quat, scale = matrix.decompose()
    return "{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}".format(quat.w, quat.x, quat.y, quat.z, pos.x, pos.y, pos.z, scale.x, scale.y, scale.z)


def output_matrix_without_scale(matrix):
    pos, quat, scale = matrix.decompose()
    return "{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}".format(quat.w, quat.x, quat.y, quat.z, pos.x, pos.y, pos.z)


def is_meta_bone(bone_name):
    return bone_name[:3] == "ik-" or bone_name[:3] == "fk-" or bone_name[0] == "_"


def find_valid_parent(armature, bone):
    parent = bone.parent

    # for override in armature.lex.getExporterOverrides():
    #     if override[0] == "Parent" and override[1] == bone.name and override[2] in armature.bones:
    #         parent = armature.bones[override[2]]
    #         break

    def is_bone_valid(b):
        return b and not is_meta_bone(b.name)
    
    while parent and not is_bone_valid(parent):
        parent = parent.parent

    return parent


def is_smooth_vertex(vert, face):
    # for edge in face.edges:
    #     if not edge.smooth and vert in edge.verts:
    #         return False

    return face.smooth

def get_vert_normal(vert, face):
    return Vec3.copy(vert.normal) if is_smooth_vertex(vert, face) else Vec3.copy(face.normal)

def enable_modifier(object, modifier_type):
    for mod in object.modifiers:
        if mod.type == modifier_type:
            mod.show_render = True
            mod.show_viewport = True


def disable_modifier(object, modifier_type):
    for mod in object.modifiers:
        if mod.type == modifier_type:
            mod.show_render = False
            mod.show_viewport = False


# =====================================================================


class Vert(Vec3):
    def __init__(self, blender_index, position):
        super(Vert, self).__init__(position.x, position.y, position.z)
        self.blender_index = blender_index


class Bone:
    def __init__(self, id, name, transform, bind_pose, parent):
        self.id = id
        self.name = name
        self.local_transform = transform
        self.bind_pose = bind_pose
        self.parent = parent

    def get_local_transform(self):
        return self.local_transform

    def get_global_transform(self):
        global_transform = self.get_local_transform()

        parent = self.parent
        while parent is not None and parent is not "":
            global_transform = parent.get_local_transform() * global_transform
            parent = parent.parent

        return global_transform


class Doodad:
    def __init__(self, name, transform):
        self.name = name
        self.transform = transform


class Face:
    def __init__(self):
        self.verts = []
        self.normals = []
        self.uvs = []


class Mesh:
    def __init__(self, mesh_object, skeleton):
        self.name = mesh_object.name
        self.verts = OrderedSet()
        self.normals = OrderedSet()
        self.uvs = OrderedSet()
        self.vbs = []
        self.faces = []

        # --- mesh with modifiers applied ---
        disable_modifier(mesh_object, 'ARMATURE')
        apply_modifiers = True
        settings = 'PREVIEW'
        mesh = mesh_object.to_mesh(bpy.context.depsgraph, apply_modifiers, calc_undeformed=True)
        enable_modifier(mesh_object, 'ARMATURE')

        if mesh_object.data and (not mesh_object.data.polygons or not mesh_object.data.uv_layers):
            active_obj = bpy.context.scene.objects.active
            selected_objects = bpy.context.selected_objects
            for o in selected_objects:
                o.select = False
                
            temp_obj = create_tmp_object("UNWRAP", mesh)
            bpy.context.scene.objects.link(temp_obj)
            temp_obj.select = True
            bpy.context.scene.objects.active = temp_obj
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.uv.smart_project()

            temp_obj.select = False
            for o in selected_objects:
                o.select = True
            bpy.context.scene.objects.active = active_obj
            bpy.data.objects.remove(temp_obj, True)

        # get triangulated mesh
        mesh_data = bmesh.new()
        mesh_data.from_mesh(mesh)
        bmesh.ops.triangulate(mesh_data, faces=mesh_data.faces)

        # initialize the face array
        for _ in mesh_data.faces:
            self.faces.append(Face())

        # verts / normals
        for face in mesh_data.faces:
            for i, vert in enumerate(face.verts):
                normal = get_vert_normal(vert, face)
                vert_idx = self.verts.add(Vert(vert.index, vert.co))
                normal_idx = self.normals.add(normal)
                self.faces[face.index].verts.append(vert_idx)
                self.faces[face.index].normals.append(normal_idx)

        # uvs
        if mesh_data.loops.layers.uv.active is not None:
            for face in mesh_data.faces:
                for vert, loop in zip(face.verts, face.loops):
                    vert_uv = loop[mesh_data.loops.layers.uv.active].uv
                    uv_idx = self.uvs.add(Vec2.copy(vert_uv))
                    self.faces[face.index].uvs.append(uv_idx)

        # vert bone weights
        if skeleton:
            for v in self.verts:
                vgroups_weights = []
                for vg in mesh.vertices[v.blender_index].groups:
                    if vg.group < len(mesh_object.vertex_groups):
                        bone_name = mesh_object.vertex_groups[vg.group].name
                        if skeleton.has_bone(bone_name):
                            vgroups_weights.append((skeleton.get_bone(bone_name).id, vg.weight))
                self.vbs.append(vgroups_weights)

        bpy.data.meshes.remove(mesh)


class Skeleton:
    def __init__(self, armature_object):
        self.transform = mathutils.Matrix()
        self.bones = []

        armature = armature_object.data
        bone_id = 0

        for bone in armature.bones:
            if not is_meta_bone(bone.name):
                bone_local = bone.matrix_local
                parent_name = ""
                parent = find_valid_parent(armature, bone)

                if parent is not None:
                    bone_local = parent.matrix_local.inverted() @ bone_local
                    parent_name = parent.name

                # get all bone ibp
                bind_pose = bone.matrix_local
                self.bones.append(Bone(bone_id, bone.name, bone_local, bind_pose, parent_name))
                bone_id += 1

        # set the bone parent data
        for bone in self.bones:
            if bone.parent:
                # convert bone name into bone object
                parent_name = bone.parent
                bone.parent = self.get_bone(parent_name)

    def get_bone(self, name):
        for bone in self.bones:
            if bone.name == name:
                return bone

    def has_bone(self, name):
        for bone in self.bones:
            if bone.name == name:
                return True
        return False


class Animation:
    def __init__(self, name, armature_obj,  bl_action, skeleton):
        self.name = name
        self.keyframes_local_space = {}
        self.keyframes_obj_space = {}
        
        self.keyframes_points = set([frame_point.co.x
                             for fcurve in bl_action.fcurves for frame_point in fcurve.keyframe_points])

        self.is_looping = bl_action.lex_export.is_looping

        self.bake(armature_obj, bl_action, skeleton)
        
    def add_pose_obj_space(self, keyframe, bone_name, global_transform):
        keyframe = int(keyframe)
        if keyframe not in self.keyframes_obj_space:
            self.keyframes_obj_space[keyframe] = {}
        self.keyframes_obj_space[keyframe][bone_name] = global_transform

    def add_pose_local_space(self, keyframe, bone_name, local_transform):
        keyframe = int(keyframe)
        if keyframe not in self.keyframes_local_space:
            self.keyframes_local_space[keyframe] = {}
        self.keyframes_local_space[keyframe][bone_name] = local_transform
        
    def bake(self, armature_obj, bl_action, skeleton):
        prev_action = armature_obj.animation_data.action
        armature_obj.animation_data.action = bl_action
    
        frame_begin, frame_end = [int(x) for x in bl_action.frame_range]
        for frame in range(frame_begin, frame_end + 1):
            bpy.context.scene.frame_set(frame)
            self.bake_pose_to_frame(frame, armature_obj.pose.bones, skeleton)

        armature_obj.animation_data.action = prev_action
 
    def bake_pose_to_frame(self, frame, pose_bones, skeleton):
        global_bone_poses = {}
        for pb in pose_bones:
            if not is_meta_bone(pb.name):
                global_bone_poses[pb.name] = pb.matrix
            
        for bone_name, global_pose in global_bone_poses.items():
            bone = skeleton.get_bone(bone_name)
            parent_pose = mathutils.Matrix()
            if bone.parent is not None and bone.parent is not "":
                parent_pose = global_bone_poses[bone.parent.name]

            local_pose = parent_pose.inverted() @ global_pose
            bone_to_pose = bone.get_local_transform().inverted() @ local_pose
            
            self.add_pose_local_space(frame, bone_name, bone_to_pose)
            self.add_pose_obj_space(frame, bone_name, global_bone_poses[bone_name])
        
        
def get_frame_in_different_range(f, old_frame_range, new_frame_range):
    old_frame_count = old_frame_range[1] - old_frame_range[0]
    new_frame_count = new_frame_range[1] - new_frame_range[0]
    assert old_frame_count > 0 and new_frame_count > 0
    normalized_frame_time = (f - old_frame_range[0]) / old_frame_count
    return round(new_frame_range[0] + (normalized_frame_time * new_frame_count))
