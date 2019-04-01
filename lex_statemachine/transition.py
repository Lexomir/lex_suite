import bpy
from .. import handlers

_object_transitions = []

class State:
    def __init__(self, location, rotation, scale):
        self.location = location
        self.rotation = rotation
        self.scale = scale

class ObjectStateTransition:
    def __init__(self, dying_components, other_components, location):
        self.dying_components = dying_components
        self.healthy_components = other_components
        self.target_state = State(location, (1,0,0,0), (1,1,1))


# when transition starts, we completely set the component list to the new ones.
# the 'transition' object adopts the old components that are dying and 
# and is now responsible for calling object_transitioning / frame_changed on them

def add_object_state_transition(next_state):
    nodegroup = next_state.get_nodegroup()
    for o in nodegroup.get_affected_objects():
        # adopt all the dying components
        dying_components = []
        for ec in o.lexeditor.components:
            also_exists_in_next_state = any(sc.filepath == ec.filepath for sc in next_state.state.editor_components_serialized)
            if also_exists_in_next_state:
                healthy_components.append(ec.get_instance())
            else:
                dying_components.append(ec.get_instance())
    
        _object_transitions.append(ObjectStateTransition(dying_components, healthy_components, next_state.location))
                

def add_scene_state_transition(prev_state, next_state):
    nodegroup = next_state.get_nodegroup()
    for s in nodegroup.get_affected_scenes():
        for os in next_state.object_states:
            add_object_state_transition(os)


def _on_frame_change_post(scene):
    for trans in _object_transitions[:]:
        # if a dying component is done, call stop on it and remove it from the list
        for dc in trans.dying_components[:]:
            setattr(dc, "fps", bpy.context.scene.render.fps)
            setattr(dc, 'f', scene.frame_current)
            dc.frame_changed()
            if hasattr(dc, "object_transitioning"):
                done = dc.object_transitioning(trans.target_state)
                if done:
                    dc.stop()
                    trans.dying_components.remove(dc)

        # transition healthy components
        for hc in trans.healthy_components[:]:
            setattr(hc, "fps", bpy.context.scene.render.fps)
            setattr(hc, 'f', scene.frame_current)
            if hasattr(hc, "object_transitioning"):
                done = hc.object_transitioning(trans.target_state)
                if done:
                    trans.healthy_components.remove(hc)

        # if all components are done transitioning, remove the transition object
        if not trans.healthy_components and not trans.dying_components:
            _object_transitions.remove[trans]



def register():
    handlers.frame_change_post_callbacks.append(_on_frame_change_post)
    
def unregister():
    handlers.frame_change_post_callbacks.remove(_on_frame_change_post)
    
        