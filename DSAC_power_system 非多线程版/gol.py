import numpy
def init():
    global fire_action
    global action_history
    fire_action=0
    action_history=numpy.array([500,500,500,500])
def get_fire_action(self):
    global fire_action
    if self.time%4==0:
        fire_action= self.action_space[0]
    else:
        self.action_space[0] =fire_action
    return fire_action
def get_history_action(action):
    global action_history
    temp=action_history
    action_history=action
    return temp