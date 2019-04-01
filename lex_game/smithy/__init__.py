import bpy


_component_update_callbacks = []

def on_component_updated(obj, component_instance):
    print('object', obj.name, 'updating component', component_instance.filepath)
    for cb in _component_update_callbacks:
        cb(obj, component_instance)

def add_component_updated_callback(func):
    _component_update_callbacks.append(func)

def remove_component_updated_callback(func):
    _component_update_callbacks.remove(func)
