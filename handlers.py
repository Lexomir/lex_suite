import bpy
from bpy.app.handlers import persistent
from .utils import *
import atexit


scene_update_callbacks = []
frame_change_post_callbacks = []
frame_change_pre_callbacks = []
data_callbacks = []
object_callbacks = []
object_name_callbacks = []
data_callbacks = []
data_name_callbacks = []
material_callbacks = []
material_name_callbacks = []
save_pre_callbacks = []
save_post_callbacks = []
load_blend_pre_callbacks = []
load_blend_post_callbacks = []
exit_callbacks = []


@persistent
def _cb_scene_update(scene):
    for cb in scene_update_callbacks: cb(scene)

    objs = bpy.context.selected_objects
    for obj in objs:
        if obj.data and obj.data.is_updated and not is_tmp_object(obj):
            for cb in data_callbacks: cb(scene, obj)

        if obj.is_updated and not is_tmp_object(obj):
            for cb in object_callbacks: cb(scene, obj)
        
        if obj.active_material and obj.active_material.is_updated:
            for cb in material_callbacks: cb(obj.active_material)


def material_name_changed(material, prev_name, new_name):
    for cb in material_name_callbacks: cb(material, prev_name, new_name)

def object_name_changed(object, prev_name, new_name):
    for cb in object_name_callbacks: cb(object, prev_name, new_name)

def data_name_changed(data, prev_name, new_name):
    for cb in data_name_callbacks: cb(data, prev_name, new_name)
    

@persistent
def _on_save_pre(context):
    for cb in save_pre_callbacks: cb(context)

@persistent
def _on_save_post(context):
    for cb in save_post_callbacks: cb(context)

@persistent
def _on_load_pre(context):
    for cb in load_blend_pre_callbacks: cb(context)

@persistent
def _on_load_post(context):
    for cb in load_blend_post_callbacks: cb(context)

@persistent
def _on_frame_change_pre(scene):
    for cb in frame_change_pre_callbacks: cb(scene)

@persistent
def _on_frame_change_post(scene):
    for cb in frame_change_post_callbacks: cb(scene)


@persistent
def _on_exit():
    for cb in exit_callbacks: cb()

def register():
    # clear
    scene_update_callbacks = []
    data_callbacks = []
    object_callbacks = []
    material_callbacks = []
    material_name_callbacks = []
    save_pre_callbacks = []
    save_post_callbacks = []
    load_blend_pre_callbacks = []
    load_blend_post_callbacks = []
    exit_callbacks = []

    bpy.app.handlers.frame_change_pre.append(_on_frame_change_pre)
    bpy.app.handlers.frame_change_post.append(_on_frame_change_post)
    bpy.app.handlers.save_pre.append(_on_save_pre)
    bpy.app.handlers.save_post.append(_on_save_post)
    bpy.app.handlers.load_pre.append(_on_load_pre)
    bpy.app.handlers.load_post.append(_on_load_post)
    atexit.register(_on_exit)

def unregister():
    bpy.app.handlers.save_pre.remove(_on_save_pre)
    bpy.app.handlers.save_post.remove(_on_save_post)
    bpy.app.handlers.load_pre.remove(_on_load_pre)
    bpy.app.handlers.load_post.remove(_on_load_post)
    bpy.app.handlers.frame_change_pre.remove(_on_frame_change_pre)
    bpy.app.handlers.frame_change_post.remove(_on_frame_change_post)
