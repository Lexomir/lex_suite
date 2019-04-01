import bpy
from .utils import *
from .engine_properties import *
from ...generic_value import GenericValue
from .utils import abs_component_scriptpath

__reload_order_index__ = -1  # register before smithy.properties.register


class LexSmithyScriptComponentInput(bpy.types.PropertyGroup, GenericValue):
    def on_value_updated(self, prev_value, curr_value):
        from . import script_parser
        obj = self.id_data
        smithy_component = obj.path_resolve(".".join(self.path_from_id().split('.')[0:-1]))
        script_parser.input_updated(smithy_component, self)

class LexSmithyScriptComponent(bpy.types.PropertyGroup):
    def get_name(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]

    def set_filepath_and_update(self, filepath):
        from . import script_parser
        if filepath != self.filepath:
            self['filepath'] = filepath
            script_parser.refresh_inputs(self)
            # TODO compute inputs

    def set_filepath(self, filepath):
        self['filepath'] = filepath

    def get_filepath(self):
        return self['filepath'] if 'filepath' in self else ""            

    def valid(self):
        return self.err_log == "" and self.filepath != ""

    def get_input(self, name):
        i = self.inputs.get(name)
        return i.get_value() if i else None
    
    def set_input(self, name, value):
        i = self.inputs.get(name)
        if i:
            i.set_value(value)

    def refresh(self):
        pass

    
    filepath : bpy.props.StringProperty(default="", set=set_filepath_and_update, get=get_filepath)
    inputs : bpy.props.CollectionProperty(type=LexSmithyScriptComponentInput)
    file_exists : bpy.props.BoolProperty(default=False)
    err_log : bpy.props.StringProperty(default="")

class LexSmithyObject(bpy.types.PropertyGroup):
    def get_component(self, filepath):
        for c in self.script_components:
            if c.filepath == filepath:
                return c
    
    def add_component(self, filepath):
        c = self.get_component(filepath)
        if not c:
            c = self.script_components.add()
            c.filepath = filepath
            self.get_component_system().refresh_inputs(c)
        return c

    def remove_component(self, filepath):
        for i, c in enumerate(reversed(self.script_components)):
            if c.filepath == filepath:
                self.script_components.remove(i)

    def get_components(self):
        return self.script_components[:]

    def get_component_system(self):
        from . import script_parser
        return script_parser
    
    active_script_component_index : bpy.props.IntProperty(default=-1)
    script_components : bpy.props.CollectionProperty(type=LexSmithyScriptComponent)
    #active_engine_component_index : bpy.props.IntProperty(default=-1)
    #engine_components : bpy.props.CollectionProperty(type=LexSmithyEngineComponent)

