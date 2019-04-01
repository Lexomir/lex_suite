import bpy
from .. import handlers
from .component import Component
import os.path
from .component import get_or_create_component
from .utils import abs_editor_scriptpath

def compile_component(bpy_component_instance):
    component = get_or_create_component(bpy_component_instance.filepath)
    component.compile()

def start_component(bpy_component_instance):
    obj = bpy_component_instance.id_data
    print("Starting component '{}' on object '{}'".format(bpy_component_instance.get_name(), obj.name))
    
    component = get_or_create_component(bpy_component_instance.filepath)

    # compile script
    compiled_successfully = True if component.is_compiled() else component.compile()
    bpy_component_instance.err_log = component.err_log
    bpy_component_instance.file_exists = component.file_exists
    
    # start component
    if compiled_successfully:
        component.start(bpy_component_instance)


def stop_component(bpy_component_instance):
    obj = bpy_component_instance.id_data
    print("Stopping component '{}' on object '{}'".format(bpy_component_instance.get_name(), obj.name))
    component = get_or_create_component(bpy_component_instance.filepath)
    component.stop(bpy_component_instance)

def update_component_input(bpy_component_instance, bpy_component_input, prev_value, curr_value):
    component = get_or_create_component(bpy_component_instance.filepath)
    obj = bpy_component_instance.id_data
    component.input_updated(obj, bpy_component_input)

def refresh_inputs(bpy_component_instance):
    component = get_or_create_component(bpy_component_instance.filepath)
    component.refresh_inputs(bpy_component_instance)    


_frame_changed = False

def _on_scene_update(scene):
    # collect used scripts
    used_component_scripts = {} 
    for obj in bpy.data.objects:
        for c in obj.lexeditor.components:
            if c.filepath != "":
                script_path = c.filepath
                instances_using_script = used_component_scripts.get(script_path, set())
                instances_using_script.add(c)
                used_component_scripts[script_path] = instances_using_script

    # compile any scripts that were modified
    for filepath, instances in used_component_scripts.items():
        component = get_or_create_component(filepath)
        if component.has_changed():
            # stop current components 
            for bpy_component_instance in instances:
                stop_component(bpy_component_instance)

            # compile script
            compiled_successfully = component.compile()

            # startup components again
            for bpy_component_instance in instances:
                bpy_component_instance.err_log = component.err_log
                bpy_component_instance.file_exists = component.file_exists
                if compiled_successfully:
                    start_component(bpy_component_instance)
        
    # process scripts that need it
    for filepath, instances in used_component_scripts.items():
        component = get_or_create_component(filepath)
        for bpy_component_instance in instances:
            if bpy_component_instance.valid():
                # process components
                global _frame_changed
                if _frame_changed:
                    obj = bpy_component_instance.id_data
                    component.frame_changed(obj)
    
    _frame_changed = False


def _on_frame_change_post(scene):
    global _frame_changed
    _frame_changed = True
    _on_scene_update(scene)

def register():
    handlers.scene_update_callbacks.append(_on_scene_update)
    handlers.frame_change_post_callbacks.append(_on_frame_change_post)

def unregister():
    handlers.scene_update_callbacks.remove(_on_scene_update)
    handlers.frame_change_post_callbacks.remove(_on_frame_change_post)
    