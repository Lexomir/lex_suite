import bpy

def create_noise_field(*args, **kwargs):
    return [[4,4,4], [5,5,5], [6,6,6]]

def create_icosphere(*args, **kwargs):
    return [[4,4,4], [5,5,5], [6,6,6]] 

def Falloff(**kwargs):
    return {}


def abs_editor_scriptpath(local_path):
    return bpy.path.abspath("//") + "editor_components/" + local_path + ".py"
