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
        enable_autopilot = False
    ) :
        self.server_ip = server_ip
        self.server_port = server_port
        self.gladius_radius = gladius_radius
        self.enable_autopilot = enable_autopilot

    def connect(self) :
        df.connect(self.server_ip, self.server_port)
        time.sleep(2) 
        df.disable_log()

    def resetGame(self) :
        self.prev_observations = None

        df.set_client_update_mode(True)
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
        rewards = self.calcReward(observations, is_done)

        return observations, is_done


    def calcObservation(self) :
        observations = {}
        for plane_name in self.planes :
            observations[plane_name] = df.get_plane_state(plane_name)

            obs = observations[plane_name]
            obs["position"] = np.array(obs["position"])
            obs["Euler_angles"] = np.array(obs["Euler_angles"])
            obs["velocity"] = np.array(obs["move_vector"])
            obs["dist_from_origin"] = np.linalg.norm(obs["position"])

        # assume only 2 aircraft.
        for plane_name, my_obs in observations.items() :
            for ennemy_plane, ennemy_obs in observations.items() :
                if ennemy_plane == plane_name :
                    continue
                
                vec_to_ennemy = ennemy_obs["position"] - my_obs["position"]
                vec_to_ennemy_norm = vec_to_ennemy / np.linalg.norm(vec_to_ennemy)
                my_direction = my_obs["velocity"] / np.linalg.norm(my_obs["velocity"])
                
                observations[plane_name]["cos_angle_to_ennemy"] = np.dot(vec_to_ennemy_norm, my_direction)
                observations[plane_name]["angle_to_ennemy"] = np.arccos(observations[plane_name]["cos_angle_to_ennemy"])
        
        return observations

    def distanceToBoundary(self, observation) :
        """
        args
            pos : list
                [, height, ]
            orientation : list
                []

        return
            distance to wall
            minus if out of boundary
        """

        position = np.array(observation["position"])
        velocity = np.array(observation["move_vector"])

        if np.linalg.norm(position, ord = 2) >= self.gladius_radius :
            return -1

        else :
            return 1

        speed = np.linalg.norm(velocity, ord = 2)
        velocity_norm = velocity / speed

        line_origin_distance = np.linalg.norm(np.outer(velocity_norm, position), ord = 2)
        base_length = np.sqrt(self.gladius_radius**2 - line_origin_distance**2)

        distance = base_length - np.dot(velocity_norm, position)

        #print("distance:", int(np.linalg.norm(position, ord = 2)), np.linalg.norm(velocity_norm))

        return distance

    def checkEpisodEnd(self, observations) :
        for plane, obs in observations.items() :
            if obs["health_level"] == 0 :
                print("zero health_level")
                return True
            if obs['destroyed'] or obs['wreck'] or obs['crashed'] :
                print("destroyed")
                return True
            if self.distanceToBoundary(obs) <= 0 :
                print("out of bound")
                return True

        return False
        
        
    def calcReward(self, observations, is_done) :
        if not self.prev_observations :
            self.prev_observations = observations
            return 0

        rewards = {}
        for plane_name, obs in observations.items() :
            reward = 0            
            prev_obs = self.prev_observations[plane_name]

            num_bullet_fired = prev_obs["num_bullet"] - obs["num_bullet"]

            reward += obs["hit_count"] * 10000
            reward += num_bullet_fired * obs["angle_to_ennemy"]**3

            # punish
            reward += num_bullet_fired * -1

            if obs["num_bullet"] == 0 :
                reward -= 1000

            reward += (prev_obs["health_level"] - obs["health_level"]) * -10000

            if obs["health_level"] == 0 or obs['destroyed'] or obs['wreck'] or self.distanceToBoundary(obs) <= 0 :
                obs["loose"] = True
                reward -= -10000
                print(plane_name, "loose")
            elif is_done :
                obs["won"] = True
                reward += 10000
                print(plane_name, "won")

            reward -= (obs["dist_from_origin"] / self.gladius_radius) ** 3 * 1000
            rewards[plane_name] = reward

            """
            print(
                "{} dist:{} fired:{} hit:{} gun_reward:{} health_diff:{} total:{}".format(
                    plane_name,
                    int(obs["dist_from_origin"]),
                    num_bullet_fired,
                    obs["hit_count"],
                    num_bullet_fired * obs["angle_to_ennemy"]**3 - num_bullet_fired * -1,
                    prev_obs["health_level"] - obs["health_level"],
                    rewards[plane_name]
                ),
                end = "     "
            )
            """

        self.prev_observations = observations
        #print()

        return rewards

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