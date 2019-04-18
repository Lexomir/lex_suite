import bpy
from ...utils import *
from . import engine_components


def entity_name(obj):
    return "{}_{}".format(get_blend_filename(), make_valid_name(obj.name))
                
def is_entity(obj):
    True

def fetch_component_definition(component_type):
    if component_type in engine_components.component_definitions:
        return engine_components.component_definitions[component_type]
    else:
        return None


def abs_component_scriptpath(local_path):
    return bpy.path.abspath("//") + "gamedata/assets/scripts/components/" + local_path + ".lua"

def abs_state_scriptpath(state_name):
    return bpy.path.abspath("//") + "gamedata/assets/scripts/states/" + state_name + ".lua"