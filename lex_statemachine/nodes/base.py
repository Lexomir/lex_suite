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
        applied_state = self.get_nodegroup().find_applied_state_node()
        if not applied_state:
            # this node will adopt the object's current state
            self.get_nodegroup().set_node_as_applied(self)
        else:
            self.get_nodegroup().apply_state(self)

        self.inputs.new('LexSM_StateSocket', "Previous")
        self.outputs.new('LexSM_StateSocket', "Next")
 
        self._call_state_created_callbacks()

    def update(self):
        for i in self.inputs:
            i.check_for_new_input()
        
        # add an extra empty input
        if self.inputs[-1].is_linked:
            self.inputs.new('LexSM_StateSocket', "Previous")
        
        # remove any empty inputs at the end (except for one)
        i = len(self.inputs) - 2
        while i >= 0 and not self.inputs[i].is_linked:
            self.inputs.remove(self.inputs[-1])
            i -= 1

    def get_input_states(self):
        return []

    def get_output_states(self):
        return []

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
        self.color = self.true_color
        self.get_nodegroup().apply_state(self)
        self._call_state_created_callbacks()

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.operator("lexsm.apply_state_node_under_cursor", text="Apply")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "lex_name", text="Name")
        layout.prop(self, "true_color", text="Color")

    def _call_state_created_callbacks(self):
        from .. import _scene_state_created_callbacks
        for cb in _scene_state_created_callbacks:
            cb(self.get_nodegroup(), self)

    true_color : bpy.props.FloatVectorProperty(subtype='COLOR', default=(0.4, 0.4, 0.4))
    is_applied : bpy.props.BoolProperty(default=False)


class LexSM_BaseNodeTree:
    
    def apply_active_state(self):
        self.apply_state(self.nodes.active)

    def set_node_as_applied(self, node):
        applied_state = self.find_applied_state_node()
        if applied_state != node:
            if applied_state:
                applied_state.color = applied_state.true_color
                applied_state.is_applied = False
            
            activated_color = (0.348079, 0.548852, 0.348826)
            node.color = activated_color
            node.use_custom_color = True
            node.is_applied = True
        
        # return the previous applied node
        return applied_state
    
    def find_applied_state_node(self):
        for n in self.nodes:
            if n.is_applied:
                return n
        return None

