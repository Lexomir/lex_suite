import bpy
import os
from .utils import abs_state_scriptpath

# external interface for lex_game.smithy
def state_script_exists(state_name):
    script_filepath = abs_state_scriptpath(state_name)
    return os.path.exists(script_filepath)

def create_state_script(state_name):
    template_filepath = os.path.normpath(os.path.abspath(os.path.dirname(__file__) + "/../templates/smithy_state_script_template.txt"))
    with open(template_filepath, "r") as template_file:
        script_template = template_file.read()

    output_filepath = abs_state_scriptpath(state_name)
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    print("Making State Script: ", output_filepath)

    with open(output_filepath, "w") as script_file:
        script_file.write(script_template)

    return output_filepath

def get_component_system():
    from . import script_parser
    return script_parser

_component_update_callbacks = []

def on_component_updated(obj, component_instance):
    for cb in _component_update_callbacks:
        cb(obj, component_instance)

def add_component_updated_callback(func):
    _component_update_callbacks.append(func)

def remove_component_updated_callback(func):
    _component_update_callbacks.remove(func)
