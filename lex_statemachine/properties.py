import bpy
from ..properties import LexStringProperty

from .. import lex_editor

__reload_order_index__ = -2




class LexSM_SerializedComponent(bpy.types.PropertyGroup):
    filepath : bpy.props.StringProperty()
    data : bpy.props.StringProperty()

    def serialize(self, bpy_component_instance):
        self.filepath = bpy_component_instance.filepath
        serialized_inputs = ""
        for i in bpy_component_instance.inputs:
            serialized_inputs += i.name + "," + i.datatype + "," + i._get_string_value() + "\n"

        self.data = serialized_inputs[:-1]  # without last '\n'

    def deserialize(self, bpy_component_instance):
        serialized_inputs = self.data
        if not serialized_inputs:
            return 

        input_strs = serialized_inputs.split('\n')
        
        c = bpy_component_instance
        c.set_filepath(self.filepath)
        c.inputs.clear()
        for input_str in input_strs:
            name, datatype, str_value = input_str.split(",", 2)
            ci = c.inputs.add()
            ci.name = name
            ci.datatype = datatype
            ci._set_string_value(str_value)
        

class LexSM_ObjectState(bpy.types.PropertyGroup):
    def get_name(self):
        return self.name

    # save object state
    def save(self, obj):
        self.editor_components_serialized.clear()
        for c in obj.lexeditor.components:
            sc = self.editor_components_serialized.add()
            sc.serialize(c)

        self.smithy_components_serialized.clear()
        for c in obj.lexgame.smithy.script_components:
            sc = self.smithy_components_serialized.add()
            sc.serialize(c)

        self.location = obj.location
        self.rotation_quaternion = obj.rotation_quaternion
        self.scale = obj.scale

        from . import _obj_save_callbacks
        for cb in _obj_save_callbacks:
            cb(obj, self)

    
    # load state into the given object
    def load(self, obj):
        replace_components(obj.lexeditor, self.editor_components_serialized)
        replace_components(obj.lexgame.smithy, self.smithy_components_serialized)

        obj.location = self.location
        obj.rotation_quaternion = self.rotation_quaternion
        obj.scale = self.scale

        from . import _obj_load_callbacks
        for cb in _obj_load_callbacks:
            cb(obj, self)


    def store_data(self, identifier, str_data):
        data = self.custom_state_data.get(identifier)
        if not data:
            data = self.custom_state_data.add()
            data.name = identifier
        data.value = str_data

    def get_data(self, identifier):
        data = self.custom_state_data.get(identifier)
        if data:
            return data.value
        return None

    smithy_components_serialized : bpy.props.CollectionProperty(type=LexSM_SerializedComponent)
    editor_components_serialized : bpy.props.CollectionProperty(type=LexSM_SerializedComponent)
    custom_state_data : bpy.props.CollectionProperty(type=LexStringProperty)
    location : bpy.props.FloatVectorProperty(size=3)
    scale : bpy.props.FloatVectorProperty(size=3)
    rotation_quaternion : bpy.props.FloatVectorProperty(size=4)


class LexSM_Object(bpy.types.PropertyGroup):
    def get_nodegroup(self):
        return bpy.data.node_groups.get(self.node_group, None)

    def get_node_group_name(self):
        # for some reason blender puts three spaces in the beginning (if you select it with prop_search)
        if self.node_group[:3] == '   ':
            return self.node_group[3:]
        else:
            return self.node_group

    node_group : bpy.props.StringProperty()


class LexSM_Scene(bpy.types.PropertyGroup):
    def get_nodegroup(self):
        from .nodes.base import LexSM_BaseNodeTree
        nodegroup = bpy.data.node_groups.get(self.node_group)
        return nodegroup if isinstance(nodegroup, LexSM_BaseNodeTree) else None

    def get_node_group_name(self):
        # for some reason blender puts three spaces in the beginning (if you select it with prop_search)
        if self.node_group[:3] == '   ':
            return self.node_group[3:]
        else:
            return self.node_group

        def add_object_save_callback(self, identifier, func):
            print("adding onsave:", identifier)

        
        def add_object_load_callback(self, identifier, func):
            print("adding onload:", identifier)



    node_group : bpy.props.StringProperty()


def replace_components(component_context, state_components):
    def component_list_intersection(a_list, b_list):
            intersecting = []
            a_list = list(a_list)
            b_list = list(b_list)
            for a in a_list:
                found_items = [b for b in b_list if b.filepath == a.filepath]
                if found_items:
                    b = found_items[0]
                    intersecting.append((a, b))
                    a_list.remove(a)
                    b_list.remove(b)
            return a_list, intersecting, b_list

    bpy_components = component_context.get_components()
    dying_components, continuing_components, new_components = component_list_intersection(bpy_components, state_components)
    for dying_c in dying_components:
        component_context.remove_component(dying_c.filepath)
    
    component_system = component_context.get_component_system()
    for (bpy_c, state_c) in continuing_components:
        state_c.deserialize(bpy_c)
        component_system.refresh_inputs(bpy_c)
    for new_sc in new_components:
        bpy_c = component_context.add_component(new_sc.filepath)
        new_sc.deserialize(bpy_c)
        component_system.refresh_inputs(bpy_c)



def register():
    bpy.types.Object.lexsm = bpy.props.PointerProperty(type=LexSM_Object)
    bpy.types.Scene.lexsm = bpy.props.PointerProperty(type=LexSM_Scene)

def unregister():
    del bpy.types.Object.lexsm
    del bpy.types.Scene.lexsm
