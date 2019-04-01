import bpy
from .utils import *


class LexSmithyEngineComponentProperty(bpy.types.PropertyGroup):
    def get_attribute_value_as_bool(self):
        return bool(self.string_value)

    def set_attribute_value_as_bool(self, val):
        self.string_value = str(val) if val else ""

    def get_attribute_value_as_float(self):
        val = 0
        try: val = float(self.string_value)
        finally: return val

    def set_attribute_value_as_float(self, val):
        self.string_value = str(val)

    def get_attribute_value_as_int(self):
        val = 0
        try: val = int(round(float(self.string_value)))
        finally: return val

    def set_attribute_value_as_int(self, val):
        self.string_value = str(val)

    def set_value_generic(self, val):
        if type(val) is bool:
            self.bool_value = val
        elif type(val) is float:
            self.float_value = val
        elif type(val) is int:
            self.int_value = val
        elif type(val) is str:
            self.string_value = val

    def value_matches_type(self, value_type):
        if value_type is bool:
            return self.string_value in ['True', ""]
        elif value_type is float:
            try:
                val = float(self.string_value)
                return True
            except:
                return False
        elif value_type is int:
            try: 
                val = int(round(float(self.string_value)))
                return True
            except:
                return False
        elif value_type is str:
            return True

    # properties
    string_value : bpy.props.StringProperty()
    bool_value : bpy.props.BoolProperty(get=get_attribute_value_as_bool, set=set_attribute_value_as_bool)
    float_value : bpy.props.FloatProperty(get=get_attribute_value_as_float, set=set_attribute_value_as_float)
    int_value : bpy.props.IntProperty(get=get_attribute_value_as_int, set=set_attribute_value_as_int)

    def draw(self, property_definition, layout):
        name, default = property_definition
        if type(default) is bool:
            layout.prop(self, "bool_value", text=name)
        elif type(default) is float:
            layout.prop(self, "float_value", text=name)
        elif type(default) is str:
            layout.prop(self, "string_value", text=name)
        elif type(default) is int:
            layout.prop(self, "int_value", text=name)



class LexSmithyEngineComponent(bpy.types.PropertyGroup):

    def type_updated(self, context):
        self.init(self.component_type)

    def init(self, component_type):
        c_def = fetch_component_definition(component_type)
        if c_def:
            self.component_id = c_def['id']

            # properties
            prop_defs = c_def['properties'].items()
            for i, (prop_name, default_value) in enumerate(prop_defs):
                p = self.properties[prop_name] if prop_name in self.properties else None
                if not p:
                    p = self.properties.add()
                    p.name = prop_name
                    p.set_value_generic(default_value)

    def valid(self):
        c_def = fetch_component_definition(self.component_type)
        return c_def is not None

    def fetch_properties(self):
        properties = []
        c_def = fetch_component_definition(self.component_type)
        prop_defs = c_def['properties'].items()
        for prop_def in prop_defs:
            prop_name, prop_default = prop_def
            p = self.properties[prop_name] if prop_name in self.properties else None
            assert p
            properties.append({'bpy_property': p, 'definition': prop_def})
        return properties
    
    # props
    component_id : bpy.props.IntProperty(default=0)
    component_type : bpy.props.StringProperty(default="health", update=type_updated)
    properties : bpy.props.CollectionProperty(type=LexSmithyEngineComponentProperty)
