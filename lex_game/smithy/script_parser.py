# import bpy
# from ... import handlers
# from ...filewatcher import FileWatcher 
# from .utils import *
# from math import inf

# def parse_input(input_str):
#     # expect format:  --$my_name(int, min, max, default)
#     def parse_int(name, *args, **kwargs):
#         kwargs.setdefault("default", 0)
#         if len(args) > 0: kwargs['min'] = args[0]
#         if len(args) > 1: kwargs['max'] = args[1]
#         if len(args) > 2: kwargs['default'] = args[2]
#         kwargs.setdefault("default", 0)
#         kwargs.setdefault("min", -inf)
#         kwargs.setdefault("max", inf)
#         return (name, 'int', kwargs['default'], [kwargs['min'], kwargs['max']]), None
#     # expect format:  --$my_name(float, min, max, default)
#     def parse_scalar(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         if len(args) > 1: kwargs['min'] = args[1]
#         if len(args) > 2: kwargs['max'] = args[2]
#         kwargs.setdefault("default", 0)
#         kwargs.setdefault("min", -inf)
#         kwargs.setdefault("max", inf)
#         return (name, 'float', float(kwargs['default']), [float(kwargs['min']), float(kwargs['max'])]), None
#     # expect format:  --$my_name(float, min, max, default)
#     def parse_vec2(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         kwargs.setdefault("default", [0,0])
#         vec = [float(v) for v in kwargs['default']]
#         return (name, 'vec2', vec, []), None
#     # expect format:  --$my_name(float, min, max, default)
#     def parse_vec3(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         kwargs.setdefault("default", [0,0,0])
#         vec = [float(v) for v in kwargs['default']]
#         return (name, 'vec3', vec, []), None
#     # expect format:  --$my_name(float, min, max, default)
#     def parse_vec4(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         kwargs.setdefault("default", [0,0,0,0])
#         vec = [float(v) for v in kwargs['default']]
#         return (name, 'vec4', vec, []), None
#     # expect format:  --$my_name(string, default)
#     def parse_string(name, *args, **kwargs):
#         kwargs.setdefault("default", "")
#         return (name, 'string', kwargs['default'], []), None
#     # expect format:  --$my_name(bool, default)
#     def parse_bool(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         kwargs.setdefault("default", False)
#         return (name, 'bool', kwargs['default'], []), None
#     # expect format:  --$my_name(object, "")
#     def parse_object(name, *args, **kwargs):
#         if len(args) > 0: kwargs['default'] = args[0]
#         kwargs.setdefault("default", False)
#         return (name, 'object', kwargs['default'], []), None
#     # expect format:  --$my_name(enum, [item1, item2], default)
#     def parse_enum(name, *args, **kwargs):
#         if len(args) > 0: kwargs['items'] = args[0]
#         if len(args) > 1: kwargs['default'] = args[1]

#         items = kwargs.get('items')
#         if not items or type(items) is not list: 
#             return (name, 'enum', "", ['BAD_ENUM']), "Enum input has no items"
        
#         default = kwargs.get('default')
#         if default not in items:
#             kwargs["default"] = items[0]

#         return (name, 'enum', str(kwargs['default']), kwargs['items']), None

#     name, remaining = input_str.split("(", 1)
#     datatype, remaining = remaining.split(",", 1)
#     param_str, end_junk = remaining.rsplit(")", 1)

#     # i dont care if you put a colon after the name
#     if name[-1] == ":": name = name[:-1]
#     parsed_input = eval("parse_{}('{}', {})".format(datatype.strip(), name.strip(), param_str.strip()))

#     return parsed_input

# def parse_script_inputs(abs_filepath):
#     print("Parsing script:", abs_filepath)
#     inputs = []
#     errors = []
#     with open(abs_filepath, 'r') as script_file:
#         for line in script_file:
#             input_prefix = "--$"
#             if line[:len(input_prefix)] == input_prefix:
#                 input_str = line[len(input_prefix):] or ""
#                 input_str = input_str.strip()
#                 try:
#                     parsed_input, err = parse_input(input_str)
#                     if err:
#                         errors.append(err)
#                     if parsed_input:
#                         inputs.append(parsed_input)
#                 except Exception:
#                     print("Error parsing component '{}'. Invalid input '{}'".format(os.path.basename(abs_filepath), input_str))
#                     errors.append("Could not parse input '{}'".format(input_str))
#             else: 
#                 break
#     return inputs, "\n".join(errors)


# # set the inputs in the ui
# def set_bpy_inputs(bpy_component, parsed_inputs):
#     # match the ui component list size to the parsed list
#     num_inputs = len(parsed_inputs)
#     while len(bpy_component.inputs) < num_inputs:
#         bpy_component.inputs.add()
#     while len(bpy_component.inputs) > num_inputs:
#         bpy_component.inputs.remove(len(bpy_component.inputs)-1)

#     from .. import inputs_from_bpy_component, override_script_inputs
#     inputs_from_ui = inputs_from_bpy_component(bpy_component)
#     inputs = override_script_inputs(base_inputs=parsed_inputs, overrides=inputs_from_ui)

#     # convert inputs to the parsed types
#     for bpy_input, new_input in zip(bpy_component.inputs, inputs):
#         i_name, i_datatype, i_value, i_args = new_input
#         bpy_input.name = i_name
#         bpy_input.set_generic(i_datatype, i_value, i_args)


# def refresh_inputs(bpy_component_instance):
#     component = get_or_create_component(bpy_component_instance.filepath)
#     recompile_component_if_changed(component)

#     bpy_component_instance.err_log = component.err_log
#     bpy_component_instance.file_exists = component.filewatcher.file_exists
#     set_bpy_inputs(bpy_component_instance, component.inputs)

#     from . import on_component_updated
#     on_component_updated(bpy_component_instance.id_data, bpy_component_instance)

# def input_updated(bpy_component_instance, bpy_input):
#     from . import on_component_updated
#     on_component_updated(bpy_component_instance.id_data, bpy_component_instance)


# class Component:
#     def __init__(self, filepath):
#         self.filepath = filepath
#         self.filewatcher = FileWatcher(abs_component_scriptpath(filepath))
#         self.inputs = {}
#         self.err_log = ""
#         self.inputs_changed = False

#     def check_file_change(self):
#         return self.filewatcher.look()

# _components = {}
# def get_or_create_component(filepath):
#     return _components.setdefault(filepath, Component(filepath))

# def get_component(filepath):
#     return _components.get(filepath)

# def get_all_component_filepaths():
#     return list(_components)


# def recompile_component_if_changed(component):
#     has_changed = component.check_file_change()
#     if has_changed:
#         # parse script inputs
#         inputs, err_log = parse_script_inputs(abs_component_scriptpath(component.filepath))
#         component.inputs = inputs
#         component.err_log = err_log
#         component.inputs_changed = True
#     return has_changed

# def _frame_change_post(scene):
#     # collect used scripts
#     used_component_scripts = {} 
#     for obj in bpy.data.objects:
#         for c in obj.lexgame.smithy.script_components:
#             if c.filepath != "":
#                 script_path = c.filepath
#                 instances_using_script = used_component_scripts.get(script_path, set())
#                 instances_using_script.add(c)
#                 used_component_scripts[script_path] = instances_using_script

#     # reparse any scripts that were modified
#     for filepath, instances in used_component_scripts.items():
#         component = get_or_create_component(filepath)
#         recompile_component_if_changed(component)
        
#         # set inputs for component instances
#         if component.inputs_changed:
#             for bpy_component_instance in instances:
#                 bpy_component_instance.err_log = component.err_log
#                 bpy_component_instance.file_exists = component.filewatcher.file_exists
#                 set_bpy_inputs(bpy_component_instance, component.inputs)
#         component.inputs_changed = False


# def register():
#     return

    
# def unregister():
#     return