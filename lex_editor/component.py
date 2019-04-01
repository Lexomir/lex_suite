import bpy
from ..filewatcher import FileWatcher 
from . import component_data_store
from .utils import *
import math
from math import *
from mathutils import *
from types import SimpleNamespace
import sys
import traceback
from math import inf
import os.path
import bmesh


_components = {}
def get_or_create_component(filepath):
    component = _components.setdefault(filepath, Component(filepath))
    return component


def select_enum(items, **kwargs):
    kwargs.setdefault('default', items[0])
    return ('enum', kwargs['default'], items)

def select_object(*args, **kwargs):
    kwargs.setdefault('default', "")
    return ('object', kwargs['default'], [])

def select_int(*args, **kwargs):
    kwargs.setdefault('default', 0)
    kwargs.setdefault('min', -inf)
    kwargs.setdefault('max', inf)
    return ('int', kwargs['default'], [kwargs['min'], kwargs['max']])

def select_bool(*args, **kwargs):
    kwargs.setdefault('default', False)
    return ('bool', kwargs['default'], [])

def select_float(*args, **kwargs):
    kwargs.setdefault('default', 0)
    kwargs.setdefault('min', -inf)
    kwargs.setdefault('max', inf)
    return ('float', kwargs['default'], [kwargs['min'], kwargs['max']])

def select_string(*args, **kwargs):
    kwargs.setdefault('default', "")
    return ('string', kwargs['default'], [])

def select_vec2(*args, **kwargs):
    kwargs.setdefault('default', [0,0])
    return ('vec2', kwargs['default'], [])

def select_vec3(*args, **kwargs):
    kwargs.setdefault('default', [0,0,0])
    return ('vec3', kwargs['default'], [])

def select_vec4(*args, **kwargs):
    kwargs.setdefault('default', [0,0,0,0])
    return ('vec4', kwargs['default'], [])


_global_ns = dict(globals())

class Component:
    def __init__(self, filepath):
        abs_filepath = abs_editor_scriptpath(filepath)
        self.filewatcher = FileWatcher(file=abs_filepath)
        self.filepath = filepath
        self.compiled_script = None
        self.script_functions = {}
        self.inputs = SimpleNamespace()
        self.keyframe_input_names = []
        self.err_log = ""
        self.file_exists = os.path.exists(abs_filepath)
    
    def valid(self):
        return self.err_log == ""

    def get_name(self):
        return self.filepath

    def should_process_on_frame_change(self):
        return True

    def has_changed(self):
        return self.filewatcher.look() 
    
    def compile(self):
        abs_filepath = abs_editor_scriptpath(self.filepath)
        self.err_log = ""
        self.file_exists = os.path.exists(abs_filepath)
        if not self.file_exists:
            self.err_log = "File not found"
        else:
            try:
                self.script_functions = {}
                self.inputs = SimpleNamespace()

                with open(abs_filepath) as f:
                    self.compiled_script = compile(f.read(), abs_filepath, 'exec')
                exec(self.compiled_script, _global_ns, self.script_functions)
                
                # determine inputs
                self.script_functions['inputs'](self.inputs)
            except SyntaxError as err:
                self.err_log = "Syntax Error"
                traceback.print_exc()

            except Exception as err:
                self.err_log = "Runtime Error"
                traceback.print_exc()
        
        has_errors = self.err_log != ""
        if has_errors:
            self.compiled_script = None
        
        return not has_errors

    def is_compiled(self):
        return self.compiled_script is not None

    def refresh_inputs(self, bpy_component_instance):
        parsed_inputs = self.inputs.__dict__.items()
        num_inputs = len(parsed_inputs)
        while len(bpy_component_instance.inputs) < num_inputs:
            bpy_component_instance.inputs.add()

        while len(bpy_component_instance.inputs) > num_inputs:
            bpy_component_instance.inputs.remove(len(bpy_component_instance.inputs)-1)

        for bpy_input, (pi_name, parsed_input) in zip(bpy_component_instance.inputs, parsed_inputs):
            # initialize bpy inputs (ui)
            pi_type, pi_default, pi_args = parsed_input
            original_bpy_datatype = bpy_input.datatype

            # set the type info so we can check if the old value is still valid
            bpy_input.set_meta(pi_type, pi_args)
            
            needs_new_val = original_bpy_datatype != pi_type or bpy_input.name != pi_name or not bpy_input.valid()
            
            bpy_input.name = pi_name
            if needs_new_val:
                bpy_input.set_generic(pi_type, pi_default, pi_args)

            # initialize instance inputs
            instance = component_data_store.get_component_instance(bpy_component_instance.id_data, self)
            setattr(instance, pi_name, bpy_input.get_value())

    def start(self, bpy_component_instance):
        instance = component_data_store.create_component_instance(bpy_component_instance.id_data, self)
        self.refresh_inputs(bpy_component_instance)
        if 'start' in self.script_functions:
            self.run_script_function('start', instance)
            
    def stop(self, bpy_component_instance):
        if 'stop' in self.script_functions:
            obj = bpy_component_instance.id_data
            instance = component_data_store.get_component_instance(obj, self)

            self.run_script_function('stop', instance)

    def run_script_function(self, func_name, instance):
        setattr(instance, "fps", bpy.context.scene.render.fps)
        setattr(instance, "f", bpy.context.scene.frame_current)
        try:
            self.script_functions[func_name](instance)
            return True
        except:
            traceback.print_exc()
            return False


    def input_updated(self, obj, bpy_input):
        instance = component_data_store.get_component_instance(obj, self)
        value = bpy_input.get_value()
        setattr(instance, bpy_input.name, value)
        self.run_script_function('input_changed', instance)

    def frame_changed(self, obj):
        instance = component_data_store.get_component_instance(obj, self)
        self.run_script_function('frame_changed', instance)

    
    def process(self, obj):
        # print("Processing component '{}' in object '{}'".format(self.get_name(), obj.name))
        pass
        

