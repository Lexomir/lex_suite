import bpy
from .base import LexSM_BaseNodeTree

from ...utils import refresh_screen_area

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class LexSM_SceneNodeTree(bpy.types.NodeTree, LexSM_BaseNodeTree):
    bl_description = "Lex Scene NodeTree"
    bl_icon = "MESH_TORUS"
    bl_idname = "LexSM_SceneNodeTree"
    bl_label = "Scene State Machine"

    def save_current_state(self):
        assert False


    def apply_state(self, node):
        assert False


class LexSM_ObjectNodeTree(bpy.types.NodeTree, LexSM_BaseNodeTree):
    bl_description = "Lex Object NodeTree"
    bl_icon = "MESH_TORUS"
    bl_idname = "LexSM_ObjectNodeTree"
    bl_label = "Object State Machine"

    @classmethod
    def poll(cls, context):
        return False

    def save_current_state(self):
        assert False

    def apply_state(self, node):
        assert False


class LexSM_ObjectNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "LexSM_ObjectNodeTree"


class LexSM_SceneNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "LexSM_SceneNodeTree"



node_categories = [
    LexSM_ObjectNodeCategory("OBJECT", "Main", items = [
        NodeItem("LexSM_ObjectStateNode"),
    ]),
    LexSM_SceneNodeCategory("SCENE", "Main", items = [
        NodeItem("LexSM_SceneStateNode"),
    ]),
]
    
