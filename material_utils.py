import bpy


def set_active_material_output(my_node):
        nodes = my_node.id_data.nodes
        for node in nodes :
            if node.type == 'OUTPUT_MATERIAL' :
                node.is_active_output = False
        my_node.is_active_output = True


def get_active_material_output(nodes):   
        for node in nodes :
            if node.type == 'OUTPUT_MATERIAL' and node.is_active_output :
                    return node
        for node in nodes :
            if node.type == 'OUTPUT_MATERIAL' :
                    return node