import bpy
from ... import handlers
from ...filewatcher import FileWatcher 
from .utils import *
from math import inf

def parse_input(input_str):
    # expect format:  --$my_name(int, min, max, default)
    def parse_int(name, *args, **kwargs):
        kwargs.setdefault("default", 0)
        if len(args) > 0: kwargs['min'] = args[0]
        if len(args) > 1: kwargs['max'] = args[1]
        if len(args) > 2: kwargs['default'] = args[2]
        kwargs.setdefault("default", 0)
        kwargs.setdefault("min", -inf)
        kwargs.setdefault("max", inf)
        return (name, 'int', kwargs['default'], [kwargs['min'], kwargs['max']]), None
    # expect format:  --$my_name(float, min, max, default)
    def parse_float(name, *args, **kwargs):
        if len(args) > 0: kwargs['min'] = args[0]
        if len(args) > 1: kwargs['max'] = args[1]
        if len(args) > 2: kwargs['default'] = args[2]
        kwargs.setdefault("default", 0)
        kwargs.setdefault("min", -inf)
        kwargs.setdefault("max", inf)
        return (name, 'float', kwargs['default'], [kwargs['min'], kwargs['max']]), None
    # expect format:  --$my_name(float, min, max, default)
    def parse_vec2(name, *args, **kwargs):
        if len(args) > 0: kwargs['default'] = args[0]
        kwargs.setdefault("default", [0,0])
        return (name, 'vec2', kwargs['default'], []), None
    # expect format:  --$my_name(float, min, max, default)
    def parse_vec3(name, *args, **kwargs):
        if len(args) > 0: kwargs['default'] = args[0]
        kwargs.setdefault("default", [0,0,0])
        return (name, 'vec3', kwargs['default'], []), None
    # expect format:  --$my_name(float, min, max, default)
    def parse_vec4(name, *args, **kwargs):
        if len(args) > 0: kwargs['default'] = args[0]
        kwargs.setdefault("default", [0,0,0,0])
        return (name, 'vec4', kwargs['default'], []), None
    # expect format:  --$my_name(string, default)
    def parse_string(name, *args, **kwargs):
        kwargs.setdefault("default", "")
        return (name, 'string', kwargs['default'], []), None
    # expect format:  --$my_name(bool, default)
    def parse_bool(name, *args, **kwargs):
        if len(args) > 0: kwargs['default'] = args[0]
        kwargs.setdefault("default", False)
        return (name, 'bool', kwargs['default'], []), None
    # expect format:  --$my_name(object, "")
    def parse_object(name, *args, **kwargs):
        if len(args) > 0: kwargs['default'] = args[0]
        kwargs.setdefault("default", False)
        return (name, 'object', kwargs['default'], []), None
    # expect format:  --$my_name(enum, [item1, item2], default)
    def parse_enum(name, *args, **kwargs):
        if len(args) > 0: kwargs['items'] = args[0]
        if len(args) > 1: kwargs['default'] = args[1]

        items = kwargs.get('items')
        if not items or type(items) is not list: 
            return (name, 'enum', "", ['BAD_ENUM']), "Enum input has no items"
        
        default = kwargs.get('default')
        if default not in items:
            kwargs["default"] = items[0]

        return (name, 'enum', kwargs['default'], kwargs['items']), None

    name, remaining = input_str.split("(", 1)
    datatype, remaining = remaining.split(",", 1)
    param_str, end_junk = remaining.rsplit(")", 1)

    # i dont care if you put a colon after the name
    if name[-1] == ":": name = name[:-1]

    parsed_input = eval("parse_{}('{}', {})".format(datatype.strip(), name.strip(), param_str.strip()))

    return parsed_input

def parse_script_inputs(abs_filepath):
    inputs = []
    errors = []
    with open(abs_filepath, 'r') as script_file:
        for line in script_file:
            input_prefix = "--$"
            if line[:len(input_prefix)] == input_prefix:
                input_str = line[len(input_prefix):]
                parsed_input, err = parse_input(input_str)
                if err:
                    errors.append(err)
                if parsed_input:
                    inputs.append(parsed_input)
            else: 
                break
    return inputs, "\n".join(errors)



def set_bpy_inputs(bpy_component, inputs):
    num_inputs = len(inputs)
    while len(bpy_component.inputs) < num_inputs:
        bpy_component.inputs.add()

    while len(bpy_component.inputs) > num_inputs:
        bpy_component.inputs.remove(len(bpy_component.inputs)-1)

    # convert inputs to the parsed types
    for bpy_input, parsed_input in zip(bpy_component.inputs, inputs):
        pi_name, pi_type, pi_default, pi_args = parsed_input
        original_bpy_datatype = bpy_input.datatype

        # set the type info so we can check if the old value is still valid
        bpy_input.set_meta(pi_type, pi_args)
        
        needs_new_val = original_bpy_datatype != pi_type or bpy_input.name != pi_name or not bpy_input.valid()
        bpy_input.name = pi_name
        if needs_new_val:
            bpy_input.set_generic(pi_type, pi_default, pi_args)


def refresh_inputs(bpy_component_instance):
    component = get_or_create_component(bpy_component_instance.filepath)
    recompile_component_if_changed(component)

    bpy_component_instance.err_log = component.err_log
    bpy_component_instance.file_exists = component.filewatcher.file_exists
    set_bpy_inputs(bpy_component_instance, component.inputs)

    from . import on_component_updated
    on_component_updated(bpy_component_instance.id_data, bpy_component_instance)

def input_updated(bpy_component_instance, bpy_input):
    from . import on_component_updated
    on_component_updated(bpy_component_instance.id_data, bpy_component_instance)


class Component:
    def __init__(self, filepath):
        self.inputs = []
        self.filepath = filepath
        self.filewatcher = FileWatcher(abs_component_scriptpath(filepath))
        self.inputs = {}
        self.err_log = ""

    def check_file_change(self):
        return self.filewatcher.look()

_components = {}
def get_or_create_component(filepath):
    return _components.setdefault(filepath, Component(filepath))


def recompile_component_if_changed(component):
    has_changed = component.check_file_change()
    if has_changed:
        # parse script inputs
        inputs, err_log = parse_script_inputs(component.filewatcher.filename)
        component.inputs = inputs
        component.err_log = err_log
    return has_changed

def _frame_change_post(scene):
    # collect used scripts
    used_component_scripts = {} 
    for obj in bpy.data.objects:
        for c in obj.lexgame.smithy.script_components:
            if c.filepath != "":
                script_path = c.filepath
                instances_using_script = used_component_scripts.get(script_path, set())
                instances_using_script.add(c)
                used_component_scripts[script_path] = instances_using_script

    # reparse any scripts that were modified
    for filepath, instances in used_component_scripts.items():
        component = get_or_create_component(filepath)
        has_changed = recompile_component_if_changed(component)
        
        # set inputs for component instances
        if has_changed:
            for bpy_component_instance in instances:
                bpy_component_instance.err_log = component.err_log
                bpy_component_instance.file_exists = component.filewatcher.file_exists
                set_bpy_inputs(bpy_component_instance, component.inputs)


def register():
    handlers.frame_change_post_callbacks.append(_frame_change_post) 

    
def unregister():
    handlers.frame_change_post_callbacks.remove(_frame_change_post) 