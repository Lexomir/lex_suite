import bpy
from collections import OrderedDict


component_definitions = OrderedDict()
component_definitions

component_definitions["flesh"] = {
    'id': 16, 
    'properties': OrderedDict([
        ("skin_thickness", 0.25),
        ("tissue_thickness", 5),
        ("skin_sensitivity", 2), # ignored lbs of pressure
        ("skin_density", 1.0),
    ])}
component_definitions["skeleton"] = {
    'id': 17, 
    'properties': OrderedDict([
        ("bone_depth", 5),
        ("bone_width", 3),
        ("impact_reduction", 8),
    ])}
component_definitions["health"] = {
    'id': 3, 
    'properties': OrderedDict([
        ("current_blood", 30),
        ("max_blood", 30),
        ("current_stress", 0),
        ("max_stress", 30),
        ("dependent_on_subsystems", True),
        ("execution_required", False)
    ])}
component_definitions["flameable"] = {
    'id': 1, 
    'properties': OrderedDict([
        ("type", 1),   # CAN_BE_LIT, PERM_ON_FIRE
        ("intensity", 1000),
        ("radius", 8),
        ("light_intensity", 35),
        ("ambient_intensity", 0.1),
        ("color_r", 0.5),
        ("color_g", 0.4),
        ("color_b", 0.34),
        ("particle_size", 0.6),
    ])}
component_definitions["container"] = {
    'id': 6, 
    'properties': OrderedDict([
        ("max_size", 8),
        ("max_weight", 30),
    ])}
component_definitions["edible"] = {
    'id': 5, 
    'properties': OrderedDict([
        ("cooked_amount", 0),
        ("food_uses", 1),
        ("hr_sustainance_cooked", 1),
        ("hr_sustainance_uncooked", 1),
        ("hr_sickness_cooked", 0),
        ("hr_sickness_uncooked", 5),
        ("hr_intoxication_cooked", 0),
        ("hr_intoxication_uncooked", 0),
    ])}
component_definitions["damage"] = {
    'id': 4, 
    'properties': OrderedDict([
    ])}
component_definitions["literature"] = {
    'id': 14, 
    'properties': OrderedDict([
    ])}
component_definitions["armor"] = {
    'id': 13, 
    'properties': OrderedDict([
        ("pure_modify_percent", 0),
        ("pure_reduction", 0),
    ])}
component_definitions["block"] = {
    'id': 10, 
    'properties': OrderedDict([
    ])}
component_definitions["door"] = {
    'id': 12, 
    'properties': OrderedDict([
        ("type", 0),
        ("open_duration", 0.02),
        ("close_duration", 0.02),
    ])}
component_definitions["ragdollable"] = {
    'id': 18, 
    'properties': OrderedDict([
        ("activated", False),
        ("type", 0), # 0 - shape, 1 - rig
        ("subtype", 0),  # same numbers as collision_shape_type if last param is 'shape'
    ])}
component_definitions["sticky"] = {
    'id': 19, 
    'properties': OrderedDict([
        ("type:", 0)
    ])}
component_definitions["proximity"] = {
    'id': 20, 
    'properties': OrderedDict([
        ("type", 0)
    ])}
component_definitions["explodable"] = {
    'id': 8, 
    'properties': OrderedDict([
        ("type:", 0), 
        ("fuse_amount", 0.2)
    ])}
component_definitions["lifespan"] = {
    'id': 9, 
    'properties': OrderedDict([
        ("type:", 0), 
        ("how_long", 0.1)
    ])}

component_enum_items = [(identifier, identifier, identifier) for identifier in component_definitions.keys()]
