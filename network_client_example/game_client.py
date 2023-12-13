import pygame
import dogfight_client as df
import time
import sys
import numpy as np

class GameClient :
    def __init__(
        self,
        server_ip,
        server_port,
        gladius_radius = 5000,
        enable_autopilot = False,
        enable_render = True,
        display_radar_in_renderless_mode = True
    ) :
        self.server_ip = server_ip
        self.server_port = server_port
        self.gladius_radius = gladius_radius
        self.enable_autopilot = enable_autopilot
        self.enable_render = enable_render
        self.display_radar_in_renderless_mode = display_radar_in_renderless_mode

    def connect(self) :
        df.connect(self.server_ip, self.server_port)
        time.sleep(2) 
        df.disable_log()

    def resetGame(self) :
        df.set_client_update_mode(True)
        df.set_renderless_mode(False if self.enable_render else True)
        df.set_display_radar_in_renderless_mode(self.display_radar_in_renderless_mode)
        self.planes = df.get_planes_list()
        self.user_plane_idx = 0

        for plane_name in self.planes :
            df.reset_machine(plane_name)
            df.set_target_id(plane_name, 1)
            if plane_name != self.planes[self.user_plane_idx] and self.enable_autopilot :
                df.activate_IA(plane_name)

        return self.planes

    def disconnectGame(self) :
        df.set_client_update_mode(False)
        df.disconnect()

    def close(self) :
        self.disconnectGame()


        
    def update(self, control_actions:dict) :
        # put control actions to plane
        for plane_name, control_action in control_actions.items() :
            df.set_plane_roll(plane_name, control_action["roll"])
            df.set_plane_pitch(plane_name, control_action["pitch"])
            df.set_plane_yaw(plane_name, control_action["yaw"])
            df.set_plane_thrust(plane_name, control_action["thrust"])
            
            if "activate_autopilot" in control_action :
                if control_action["activate_post_combustion"] :
                    df.activate_post_combustion(plane_name)
                if control_action["deactivate_post_combustion"] :
                    df.deactivate_post_combustion(plane_name)
            if control_action["fire_machine_gun"] :
                df.fire_machine_gun(plane_name)
            else :
                df.cease_machine_gun(plane_name)

            if "camera_angle" in control_action :
                df.rotate_fix_cockpit_camera(*control_action["camera_angle"])
            if "flag_renderless_mode" in control_action :
                df.set_renderless_mode(
                    control_action["flag_renderless_mode"]
                )
            if "quit_game" in control_action :
                if control_action["quit_game"] :
                    self.close()
                    sys.exit()

        df.update_scene()

        observations = self.calcObservation()
        is_done = self.checkEpisodEnd(observations)
        return observations, is_done

    def calcObservation(self) :
        observations = {}
        for plane_name in self.planes :
            observations[plane_name] = df.get_plane_state(plane_name)

            obs = observations[plane_name]
            obs["position"] = np.array(obs["position"])
            obs["rotation"] = np.array(obs["Euler_angles"])
            obs["velocity"] = np.array(obs["move_vector"])
            obs["velocity_norm"] = obs["velocity"] / np.linalg.norm(obs["velocity"])
            obs["dist_from_origin"] = np.linalg.norm(obs["position"])
        return observations

    def checkEpisodEnd(self, observations) :
        for plane, obs in observations.items() :
            if obs["health_level"] == 0 :
                #print("zero health_level")
                return True
            if obs['destroyed'] or obs['wreck'] or obs['crashed'] :
                print("destroyed")
                return True
        return False
        
    def velocityToFixedAngle(self, v_move) :
        v_move = np.array(v_move)
        speed = np.linalg.norm(v_move, ord =2)
        v_move /= speed

    def printObservation(self, observations) :
        for plane_name, obs in observations.items() :
            position = np.array(obs[plane_name]["position"])
            angles   = np.array(obs[plane_name]["Euler_angles"])
            
            velocity = np.array(obs[plane_name]["move_vector"])
            speed = np.linalg.norm(velocity, ord =2)
            velocity_norm = velocity / speed

            line_origin_distance = np.outer(velocity_norm, position)
            base_length = np.sqrt(self.gladius_radius**2 - line_origin_distance**2)

        
if __name__ == "__main__":
    
    SERVER_IP = "192.168.219.101"
    SERVER_PORT = 50888
    
    game_client = GameClient(SERVER_IP, SERVER_PORT)
    
    while True :
        pass