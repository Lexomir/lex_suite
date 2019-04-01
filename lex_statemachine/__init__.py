'''
Depends on lex_editor and lex_game
'''

from .. import lex_editor
from .. import lex_game


_obj_save_callbacks = []
_obj_load_callbacks = []
def add_object_save_callback(func):
    _obj_save_callbacks.append(func)

def add_object_load_callback(func):
    _obj_load_callbacks.append(func)


_scene_save_callbacks = []
_scene_load_callbacks = []
def add_scene_save_callback(func):
    _scene_save_callbacks.append(func)
    
def add_scene_load_callback(func):
    _scene_load_callbacks.append(func)