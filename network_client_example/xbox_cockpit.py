import pygame
import dogfight_client as df
import time
import sys
import numpy as np

class Button :
    def __init__(self, name, idx) :
        self.name = name
        self.idx  = idx
        
        self.value = 0
        self.prev_value = 0
        self.pressed = False
        self.released = False

    def update(self, value) :
        self.prev_value = self.value
        self.value = value

        if self.prev_value == 0 and self.value == 1 :
            self.pressed = True
        elif self.prev_value == 1 and self.value == 0 :
            self.released = True
        
        elif self.prev_value == 1 and self.value == 1 :
            self.released = False
            self.pressed = False
        elif self.prev_value == 0 and self.value == 0 :
            self.pressed = False
            self.released = False

class HatButton :
    def __init__(self, name, calcValue) :
        self.name = name
        self.calcValue = calcValue

        self.value = 0
        self.prev_value = 0
        self.pressed = False
        self.released = False

    def update(self, raw_value:tuple) :
        value = self.calcValue(raw_value)

        self.prev_value = self.value
        self.value = value

        if self.prev_value == 0 and self.value == 1 :
            self.pressed = True
        elif self.prev_value == 1 and self.value == 0 :
            self.released = True
        
        elif self.prev_value == 1 and self.value == 1 :
            self.released = False
            self.pressed = False
        elif self.prev_value == 0 and self.value == 0 :
            self.pressed = False
            self.released = False

class AnalogButton :
    def __init__(self, name, idx) :
        self.name = name
        self.idx = idx
        self.value = 0

    def update(self, value) :
        if value > 0.01 or value < -0.01 :
            self.value = value
        else :
            self.value = 0

class XboxPad :
    button_name_idx_map = {
        'a':0, 'b':1, 'x':2, 'y':3,
        'lb':4, 'rb':5, 'ls':8, 'rs':9,
    }
    analog_button_idx_map = {
        'llr':0, 'lud':1,
        'rlr':2, 'rud':3,
        'lt':4,  'rt':5,
    }
    hat_button_name_func_map = {
        "left"  : lambda x : 1 if x[0] == -1 else 0,
        "right" : lambda x : 1 if x[0] ==  1 else 0,
        "up"    : lambda x : 1 if x[1] ==  1 else 0,
        "down"  : lambda x : 1 if x[1] == -1 else 0
    }

    def __init__(self) :
        self.joysticks = {}

        self.curr_state = {
            "buttons" : {
                idx: Button(name, idx) for name, idx in XboxPad.button_name_idx_map.items()
            },
            "analog_buttons" : {
                idx:AnalogButton(name, idx) for name, idx in XboxPad.analog_button_idx_map.items()
            },
            "hat_buttons" : {
                name:HatButton(name, calcValueF) for name, calcValueF in XboxPad.hat_button_name_func_map.items()
            }
        }

    def read(self) :
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                #print("Joystick button pressed.")
                if event.button == 0:
                    joystick = self.joysticks[event.instance_id]
                    if joystick.rumble(0, 0.7, 500):
                        pass
                        #print(f"Rumble effect played on joystick {event.instance_id}")

            if event.type == pygame.JOYBUTTONUP:
                pass
                #print("Joystick button released.")

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                #print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del self.joysticks[event.instance_id]
                #print(f"Joystick {event.instance_id} disconnected")

        # Get count of joysticks.
        joystick_count = pygame.joystick.get_count()

        # For each joystick:
        for joystick in self.joysticks.values() :
            jid = joystick.get_instance_id()
            name = joystick.get_name()
            guid = joystick.get_guid()
            power_level = joystick.get_power_level()

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other. Triggers count as axes.
            axes = joystick.get_numaxes()
           
            for i in range(axes):
                axis = joystick.get_axis(i) # axis is value
                if i in self.curr_state["analog_buttons"] :
                    self.curr_state["analog_buttons"][i].update(axis)

            buttons = joystick.get_numbuttons() 
            for i in range(buttons):
                button = joystick.get_button(i) # button is value
                if i in self.curr_state["buttons"] :
                    self.curr_state["buttons"][i].update(button)

            hats = joystick.get_numhats()
            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)
            for hat_button in self.curr_state["hat_buttons"].values() :
                hat_button.update(hat)

class XboxCockpit :
    def __init__(self) :
        pygame.init()
        self.xbox_pad = XboxPad()
        self.prev_thrust = 0

        self.flag_renderless_mode = -1

    def update(self) :
        self.xbox_pad.read()
        controller_state = self.xbox_pad.curr_state

        roll  = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["rlr"]].value * -1.5
        pitch = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["rud"]].value * -1.5
        yaw_l = max(controller_state["analog_buttons"][XboxPad.analog_button_idx_map["lt"]].value + 0.98, 0) * -0.7
        yaw_r = max(controller_state["analog_buttons"][XboxPad.analog_button_idx_map["rt"]].value + 0.98, 0) * 0.7
        yaw = yaw_l + yaw_r
        '''
        if yaw_l < 0 :
            yaw = yaw_l
        if yaw_r > 0 :
            yaw = yaw_r
        '''

        # control view
        fix_rot_x = 0
        fix_rot_y = 0
        fix_rot_x = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["lud"]].value * np.pi
        fix_rot_y = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["llr"]].value * np.pi
        
        fire_machine_gun = False
        if controller_state["buttons"][XboxPad.button_name_idx_map["rb"]].value :
            fire_machine_gun = True
        
        accellerate = 0
        if controller_state["hat_buttons"]["up"].value :
            accellerate += 0.01
        if controller_state["hat_buttons"]["down"].value :
            accellerate -= 0.01
        thrust = max(0, min(1, self.prev_thrust + accellerate))
        self.prev_thrust = thrust

        activate_post_combustion = False
        if controller_state["hat_buttons"]["left"].value :
            activate_post_combustion = True
        deactivate_post_combustion = False
        if controller_state["hat_buttons"]["right"].value :
            deactivate_post_combustion = True
        
        quit_game = controller_state["buttons"][XboxPad.button_name_idx_map["x"]].pressed
        
        if controller_state["buttons"][XboxPad.button_name_idx_map["a"]].pressed :
            self.flag_renderless_mode *= -1

        control_action = {}
        control_action["roll"]  = roll
        control_action["pitch"] = pitch
        control_action["yaw"]   = yaw
        control_action["thrust"] = thrust
        control_action["camera_angle"] = [fix_rot_x, fix_rot_y]
        control_action["fire_machine_gun"] = fire_machine_gun
        control_action["activate_post_combustion"] = activate_post_combustion
        control_action["deactivate_post_combustion"] = deactivate_post_combustion
        control_action["quit_game"] = quit_game
        control_action["flag_renderless_mode"] = True if self.flag_renderless_mode > 0 else False

        return control_action

if __name__ == "__main__":
    
    xbox_cockpit = XboxCockpit()

    while True :
        control_action = xbox_cockpit.update()

        print(control_action)

        time.sleep(1 / 120)


    pygame.quit()