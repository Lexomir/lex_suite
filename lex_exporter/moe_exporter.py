import bpy
import os
from ..utils import *
from .types import Mesh, Skeleton

def is_moe_exportable(obj):
    return obj.type == 'MESH'


def export_mesh_objects_as_moe(objs, export_context):
    unique_mesh_objects = [obj for obj in get_unique_mesh_objects(objs)
                               if is_moe_exportable(obj)]

    for obj in unique_mesh_objects:
            model_name = make_valid_name(obj.data.name)
                
            armature = get_affecting_armature(obj)
            skeleton = None

            if armature:
                skeleton = Skeleton(armature)

            mesh = Mesh(obj, skeleton)

            moe_abs_filepath = export_context.moe_abs_filepath_of_mesh(obj.data)
            export_moe(mesh, skeleton, moe_abs_filepath, export_context)


def export_moe(mesh, skeleton, filepath, export_context):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as file:
        print("exporting:", mesh.name, "to", filepath)
        assert len(mesh.verts) > 0
        assert len(mesh.normals) > 0 
        assert len(mesh.uvs) > 0
        
        export_options = export_context.options
        
        for vert in mesh.verts:
            x, y, z = export_context.convert_vector(vert.round(5))
            file.write('v\t{:.6f}\t{:.6f}\t{:.6f}\n'.format(x, y, z))
                
        for norm in mesh.normals:
            x, y, z = export_context.convert_vector(norm.round(5))
            file.write('vn\t{:.6f}\t{:.6f}\t{:.6f}\n'.format(x, y, z))
                
        for uv in mesh.uvs:
            file.write('vt\t{:.6f}\t{:.6f}\n'.format(uv.x, uv.y))
            
        if skeleton:
            for vb in mesh.vbs:
                normalized_weights = normalize_weights(vb)
                file.write('vb')
                count = 0
                for bone_weight in normalized_weights:
                    bone_id, weight = bone_weight
                    file.write('\t{}\t{:.6f}'.format(bone_id, weight))
                    count += 1
                while count < 3:
                    file.write('\t{}\t{}'.format('0', '0'))
                    count += 1
                file.write('\n')
            
        # faces   
        file.write('mesh {} cjWhyDoIneedToPutThisHereFuck\n'.format(mesh.name))
        for face in mesh.faces:
            file.write("f")
            for vert, uv, normal in zip(face.verts, face.uvs, face.normals):
                file.write("\t{}/{}/{}".format(vert + 1, uv + 1, normal + 1))
            file.write("\n")
            
        # skeleton
        if skeleton:
            skel_transform = export_context.convert_matrix(skeleton.transform)
                
            file.write("skeleton\t{}\n".format(serialize_quat_transform(skel_transform)))
            
            for bone in skeleton.bones:
                bone_local_transform = export_context.convert_matrix(bone.local_transform)
                    
                file.write("b\t{}\t{}\n".format(
                    make_valid_bone_name(bone.name), 
                    serialize_quat_transform_without_scale(bone_local_transform)))
                
            for bone in skeleton.bones:
                ibp = export_context.convert_matrix(bone.bind_pose.inverted())
                    
                if ExportOptions.MATRIX_IBP & export_options:
                    file.write("ibp\t{}\n".format(serialize_matrix_transform(ibp)))
                else:
                    file.write("ibp\t{}\n".format(serialize_quat_transform_without_scale(ibp)))
                
            for bone in skeleton.bones:
                parent_id = bone.parent.id if bone.parent else -1
                file.write("bp\t{}\t{}\n".format(bone.id, parent_id))