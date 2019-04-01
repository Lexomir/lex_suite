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

# load and reload submodules
##################################

from . import auto_load

auto_load.init()


# register
##################################


def register():
    auto_load.register()
    print("Registered {} with {} modules".format(bl_info["name"], len(auto_load.modules)))

    lex_suite = sys.modules[__name__]
    lex2d = sys.modules.get('lex2d')
    if lex2d:
        callback = getattr(lex2d, '__lex_suite_registered__')
        if callback: callback(lex_suite)

def unregister():
    auto_load.unregister()

    print("Unregistered {}".format(bl_info["name"]))
