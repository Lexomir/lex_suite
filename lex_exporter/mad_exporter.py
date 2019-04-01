import bpy
from ..utils import *



def export_mad(animation, skeleton, filepath, export_context, frame_range=(float("-inf"), float("inf"))):
    if animation:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as file:
            # all frames
            frames = list(animation.keyframes_local_space.keys())
            frames.sort()

            assert len(frames) > 0

            # clamp the frame range to the frames we have available
            min_frame, max_frame = frame_range
            min_frame = max(min_frame, frames[0])
            max_frame = min(max_frame, frames[len(frames)-1])
            
            file.write("is_looping\t{}\n".format(int(animation.is_looping)))
            if animation.is_looping:
                max_frame -= 1
            
            for bone in skeleton.bones:
                parent_name = bone.parent.name if bone.parent else "~"
                file.write("bp\t{}\t{}\n".format(
                    make_valid_bone_name(bone.name), 
                    make_valid_bone_name(parent_name)))

            # used for checking if the frames quat is flipped from last frame
            prev_quats = {}

            # output pose keyframes
            for frame in frames:
                if frame < min_frame:
                    continue
                if frame > max_frame:
                    break
                
                fps = bpy.context.scene.render.fps
                frame_time = ((frame - min_frame) / fps) * 1000
                file.write("t\t{}\n".format(frame_time))

                bone_poses = animation.keyframes_local_space[frame]

                for bone_name, delta_bone_pose in bone_poses.items():
                    bl_bone_pose = skeleton.get_bone(bone_name).get_local_transform() @ delta_bone_pose
                    bone_pose = export_context.convert_matrix(bl_bone_pose)

                    pos, quat, scale = bone_pose.decompose()

                    # check if the quat flipped since last frame
                    if bone_name in prev_quats:
                        previous_quat = prev_quats[bone_name]
                        flipped_quat_test = previous_quat.dot(quat)
                        if flipped_quat_test < 0:
                            quat *= -1
                    prev_quats[bone_name] = quat

                    if export_context.options & ExportOptions.EULER_MATRIX:
                        file.write("b\t{}\t{}\n".format(make_valid_bone_name(bone_name), serialize_matrix_transform(bone_pose)))
                    else:
                        file.write("b\t{}\t{}\n".format(make_valid_bone_name(bone_name), serialize_quat_from_decomposed(pos, quat, scale)))

            file.write("loop 1000")