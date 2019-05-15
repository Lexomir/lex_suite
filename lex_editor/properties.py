import bpy
from bpy.props import *
import os.path
from .component import get_or_create_component
from . import editor
from ..generic_value import GenericValue 


class BpyComponentInput(bpy.types.PropertyGroup, GenericValue):
    def on_value_updated(self, prev_value, curr_value):
        obj = self.id_data
        bpy_component = obj.path_resolve(".".join(self.path_from_id().split('.')[0:-1]))
        editor.update_component_input(bpy_component, self, prev_value, curr_value)


class BpyComponent(bpy.types.PropertyGroup):
    def valid(self):
        return self.err_log == "" and self.filepath != ""

    def get_name(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]

    def set_filepath(self, filepath):
        self['filepath'] = filepath

    def get_filepath(self):
        return self['filepath'] if 'filepath' in self else ""

    def get_input(self, name):
        i = self.inputs.get(name)
        return i.get_value() if i else None
        
    def set_input(self, name, value):
        i = self.inputs.get(name)
        if i:
            i.set_value(value)
    
    def refresh(self):
        editor.stop_component(self)
        editor.start_component(self)

    # called when component is modified externally (e.g. from statemachine)
    def refresh_inputs(self):
        editor.stop_component(self)
        editor.start_component(self)
    
    def set_filepath_and_update(self, filepath):
        if filepath != self.filepath:
            editor.stop_component(self)
            self['filepath'] = filepath
            editor.start_component(self)
    
    filepath : StringProperty(default="", set=set_filepath_and_update, get=get_filepath)
    inputs : CollectionProperty(type=BpyComponentInput)
    file_exists : BoolProperty(default=False)
    err_log : StringProperty()


class LexEditor(bpy.types.PropertyGroup):
    def get_component(self, filepath):
        for c in self.components:
            if c.filepath == filepath:
                return c
    
    def add_component(self, filepath):
        c = self.get_component(filepath)
        if not c:
            c = self.components.add()
            c.filepath = filepath
            self.get_component_system().refresh_inputs(c)
        return c
    
    def remove_component(self, filepath):
        for i, c in reversed(list(enumerate(self.components))):
            if c.filepath == filepath:
                self.components.remove(i)

    def get_components(self):
        return self.components[:]

    def get_component_system(self):
        from . import editor
        return editor

    components : CollectionProperty(type=BpyComponent)
    active_component_index : IntProperty(default=0)



def register():
    bpy.types.Object.lexeditor = PointerProperty(type=LexEditor)

    def set_bmesh(self, bm):
        if self.type == "MESH":
            bm.to_mesh(self.data)
            self.data = self.data
    bpy.types.Object.set_bmesh = set_bmesh
    
def unregister():
    del bpy.types.Object.lexeditor
