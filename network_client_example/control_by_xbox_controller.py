import pygame
import dogfight_client as df
import time
import sys

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


class AnalogButton :
    def __init__(self, name, idx) :
        self.name = name
        self.idx = idx
        self.value = 0

    def update(self, value) :
        self.value = value

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

    def __init__(self) :
        self.joysticks = {}

        self.curr_state = {
            "buttons" : {
                idx: Button(name, idx) for name, idx in XboxPad.button_name_idx_map.items()
            },
            "analog_buttons" : {
                idx:AnalogButton(name, idx) for name, idx in XboxPad.analog_button_idx_map.items()
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

class GameClient :
    def __init__(self, server_ip, server_port) :
        df.connect(server_ip, server_port)
        time.sleep(2)

        self.planes = df.get_planes_list()
        self.plane_idx = 0

        df.reset_machine(self.planes[self.plane_idx])

        df.deactivate_plane_easy_steering(self.planes[self.plane_idx])

        df.set_client_update_mode(True)

    def step(self, controller_state) :
        
        roll  = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["rlr"]].value * -1
        pitch = controller_state["analog_buttons"][XboxPad.analog_button_idx_map["rud"]].value * -1
        #yaw   = controller_state["analog_buttons"][XboxPad.analog_button_idx_map]

        deccellerate = controller_state["buttons"][XboxPad.button_name_idx_map["lb"]].value
        accellerate  = controller_state["buttons"][XboxPad.button_name_idx_map["rb"]].value
        thrust_level = df.get_plane_thrust(self.planes[self.plane_idx])
        if deccellerate :
            df.set_plane_thrust(self.planes[self.plane_idx], level = max(1, thrust_level["thrust_level"] - 0.1))
        if accellerate :
            df.set_plane_thrust(self.planes[self.plane_idx], level = max(1, thrust_level["thrust_level"] + 0.1))



        df.set_plane_pitch(
            self.planes[self.plane_idx],
            level = pitch
        )
        df.set_plane_roll(
            self.planes[self.plane_idx],
            level = roll
        )

        df.update_scene()

        state = df.get_plane_state(self.planes[self.plane_idx])
        print(state)

        if controller_state["buttons"][XboxPad.button_name_idx_map["x"]].pressed :
            self.close()
            sys.exit(0)

    def close(self) :
        df.set_client_update_mode(False)
        df.disconnect()

if __name__ == "__main__":
    
    SERVER_IP = "172.20.80.1"
    SERVER_PORT = 50888
    
    pygame.init()

    xbox_controller = XboxPad()
    
    game_client = GameClient(
        SERVER_IP, SERVER_PORT
    )

    """
    planes = df.get_planes_list()
    print(str(planes))    
    """
    
    while True :
        xbox_controller.read()

        game_client.step(xbox_controller.curr_state)
        
        time.sleep(1 / 120)

        for idx, button in xbox_controller.curr_state["buttons"].items() :
            if button.pressed :
                print(f"{button.name} pressed")
            if button.released :
                print(f"{button.name} released")
                
        """
        for idx, analog_button in xbox_controller.curr_state[
            "analog_buttons"
        ].items() :
            print(f"{analog_button.value:.3f}", end = " ")
        print()
        """




    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()