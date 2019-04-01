import bpy
from .base import LexSM_BaseNodeTree

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class LexSM_SceneNodeTree(bpy.types.NodeTree, LexSM_BaseNodeTree):
    bl_description = "Lex Scene NodeTree"
    bl_icon = "MESH_TORUS"
    bl_idname = "LexSM_SceneNodeTree"
    bl_label = "Scene State Machine"

    def find_affected_scenes(self):
        return [s for s in bpy.data.scenes if s.lexsm.get_node_group_name() == self.name]

    def save_current_state(self):
        applied_node = self.find_applied_state_node()
        if not applied_node:
            return

        scenes = self.find_affected_scenes()
        if not scenes: 
            return 

        # find source scene
        source_scene = scenes[0]
        for s in scenes:
            if s == bpy.context.scene:
                source_scene = s
                break

        # save the current state of the source scene
        applied_node.save_scene_state(source_scene)


    def apply_state(self, node):
        previously_applied_node = self.set_node_as_applied(node)

        scenes = self.find_affected_scenes()
        if not scenes: 
            return 

        # save state
        if previously_applied_node:
            # find source scene
            source_scene = scenes[0]
            for s in scenes:
                if s == bpy.context.scene:
                    source_scene = s
                    break

            # save the current state of the source scene
            previously_applied_node.save_scene_state(source_scene)

        # load new state
        for s in scenes:
            node.load_scene_state(s)


class LexSM_ObjectNodeTree(bpy.types.NodeTree, LexSM_BaseNodeTree):
    bl_description = "Lex Object NodeTree"
    bl_icon = "MESH_TORUS"
    bl_idname = "LexSM_ObjectNodeTree"
    bl_label = "Object State Machine"

    def find_affected_objects(self):
        return [o for o in bpy.data.objects if o.lexsm.get_node_group_name() == self.name]

    def save_current_state(self):
        applied_node = self.find_applied_state_node()

        if not applied_node:
            return 

        objs = self.find_affected_objects()
        if not objs: 
            return 

        # find source object
        source_object = objs[0]
        for o in objs:
            if o == bpy.context.active_object:
                source_object = o
                break
        
        applied_node.object_state.save(source_object)


    def apply_state(self, node):
        previously_applied_node = self.set_node_as_applied(node)

        objs = self.find_affected_objects()
        if not objs: 
            return 

        # save state
        if previously_applied_node:
            # find source object
            source_object = objs[0]
            for o in objs:
                if o == bpy.context.active_object:
                    source_object = o
                    break

            # save the current state of the source object
            previously_applied_node.object_state.save(source_object)

        # load new state
        for o in objs:
            node.object_state.load(o)



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
    

def register():
    nodeitems_utils.register_node_categories("LexSM_NODES", node_categories)
    

def unregister():
    nodeitems_utils.unregister_node_categories("LexSM_NODES")