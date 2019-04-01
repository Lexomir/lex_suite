def inputs(self):
    self.k = keyframe()

def should_process(self):
    return False

def on_transition(self, target):
    target.location.x
    return False

def on_process(self, scene=False):
    self.object.location.x = 8 * math.sin(.001 * self.k * 180 / 3.14)
    self.object.location.y = 1

def on_start(self):
    pass

def on_stop(self):
    pass

            
# real stuff

# def on_start(self):
#     self.intense_map = map()

# def on_input_change(self):
#     self.input_dependent_map = some_map($i(0,2))

# def on_process(self):
#     supple = $i(0,100)
#     p_types = $e("sup", "um", "iDontThinkSo")
#     name = $s("sup")
#     obj = $o("daddy")
    
#     pumps = dup(scene.objects['Pumper'], 2000)
#     for pump in pumps:
#         pump.location = ($i(0,10) * rand(), supple * rand(), rand())