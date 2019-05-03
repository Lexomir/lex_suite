import bpy
from ..properties import LexSM_SerializedComponent

class LexSM_StateSocket(bpy.types.NodeSocket):
    bl_idname = "LexSM_StateSocket"
    bl_label = "State Socket"

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=text)
        else:
            layout.label(text=text)

    @property
    def connected_nodes(self):
        if not self.is_output:
            if len(self.links) > 0:
                return [self.links[0].from_node]
        else:
            return [l.to_node for l in self.links]

    # Socket color
    def draw_color(self, context, node):
        return (1,1,1,1)

    def check_for_new_input(self):
        assert not self.is_output
        input_node_name = self.links[0].from_node.name if len(self.links) > 0 else ""
        input_node_changed = input_node_name != self.prev_input_node_name
        self.prev_input_node_name = input_node_name
        return input_node_changed

    # properties
    prev_input_node_name : bpy.props.StringProperty()
    

class LexSM_BaseStateNode:
    def init(self, context):        
        return

    def update(self):
        return

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'LexSM_NodeTree'

    def get_nodegroup(self):
        return self.id_data

    def get_receiving_nodes(self):
        receiving_nodes = set()
        for o in self.outputs:
            for link in o.links:
                receiving_nodes.add(link.to_node)
        return receiving_nodes

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        return

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        return

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        return

    true_color : bpy.props.FloatVectorProperty(subtype='COLOR', default=(0.4, 0.4, 0.4))
    is_applied : bpy.props.BoolProperty(default=False)


class LexSM_BaseNodeTree:
    pass
