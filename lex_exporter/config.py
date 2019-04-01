import bpy
import os
import json
from .. import utils


# returns nil if no root exists
def get_game_runtime_root():
    return os.environ.get('LEX_GAME_ROOT')

def get_asset_root():
    return os.environ.get('LEX_ASSET_ROOT')

def get_local_image_dir():
    return '//textures'

def get_blend_filename_for_data(data):
    if utils.is_externally_linked(data):
        filename_with_extention = bpy.path.basename(data.library.filepath)
        return os.path.splitext(filename_with_extention)[0]
    else:
        return get_blend_filename()


