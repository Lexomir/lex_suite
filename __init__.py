'''
Copyright (C) 2018 lexomir
lexomir@gmail.com

Created by lexomir

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Lex Suite",
    "description": "",
    "author": "lexomir",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "This addon will explode in 60 seconds",
    "wiki_url": "",
    "category": "Scene" }


import bpy

import os
import sys
import addon_utils

this_module = sys.modules[__name__]

# load and reload submodules
##################################

from . import auto_load

auto_load.init()


# register
##################################

# ===========================================================
#   Interface for connecting to external modules ('lex2d')

this_module._waiting_for_lex2d = True

def waiting_for_module(name):
    return name == "lex2d" and this_module._waiting_for_lex2d

# connection attempted by lex2d
def request_module_connection(module):
    if module.__name__ == "lex2d" and this_module.__addon_enabled__ and this_module._waiting_for_lex2d:
        this_module._waiting_for_lex2d = False
        module.connect_module(this_module)
        return True
    return False

# connection attempted by lex2d
def request_module_disconnection(module):
    if module.__name__ == "lex2d":
        this_module._waiting_for_lex2d = True
        module.disconnect_module(this_module)
        return True
    return False
# ===========================================================

# trying to connect to lex_suite
def _try_connect_to_module(name):
    other_module = sys.modules.get(name)
    connected_to_lex2d = other_module and other_module.waiting_for_module(__name__)
    if connected_to_lex2d:
        other_module.connect_module(this_module)
    this_module._waiting_for_lex2d = not connected_to_lex2d
    return connected_to_lex2d

def register():
    auto_load.register()
    print("Registered {} with {} modules".format(bl_info["name"], len(auto_load.modules)))

    _try_connect_to_module("lex2d")

def unregister():
    auto_load.unregister()

    print("Unregistered {}".format(bl_info["name"]))
