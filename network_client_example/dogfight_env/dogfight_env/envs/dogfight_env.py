import pygame
import dogfight_client as df
import time
import sys
import numpy as np

import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from gymnasium import spaces

from game_client import GameClient

class DogfightEnv(gym.Env) :
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(
        self,
        server_ip,
        server_port,
        gladius_radius = 5000,
        enable_builtin_autopilot = False,
        render_mode = None,
    ) :
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        
        self.gladius_radius = gladius_radius
        self.render_mode = render_mode

        init_observation = lambda : spaces.Dict({
            "position"          : spaces.Box(np.float64([-gladius_radius]*3), np.float64([gladius_radius]*3), shape=(3,), dtype=np.float64),
            "rotation"          : spaces.Box(np.float64([-180]*3), np.float64([180]*3), shape=(3,), dtype=np.float64),
            #"Euler_angles"      : spaces.Box(np.float64([-2*np.pi]*3), np.float64([2*np.pi]*3), shape=(3,), dtype=np.float64),
            "velocity"          : spaces.Box(np.float64([-2000]*3), np.float64([2000]*3), shape=(3,), dtype=np.float64),
            "velocity_norm"     : spaces.Box(np.float64([-1]*3), np.float64([1]*3), shape=(3,), dtype=np.float64),
            "dist_from_origin"  : spaces.Box(np.float64([0]), np.float64([gladius_radius]), dtype=np.float64),
            "angle_to_enemy"    : spaces.Box(np.float64([-np.pi]), np.float64([np.pi]), dtype=np.float64),
            "num_bullet"        : spaces.Box(0, 100000, dtype=np.uint32),
            "hit_count"         : spaces.Box(0, 255, dtype=np.uint8),
            "health_level"      : spaces.Box(np.float64([0]), np.float64([1]), dtype=np.float64),
            "loose"             : spaces.Discrete(2),
            "won"               : spaces.Discrete(2)
        })
        init_action = lambda : spaces.Dict({    
            "roll"  : spaces.Box(low=-1.0, high=1.0, dtype=np.float64),
            "pitch" : spaces.Box(low=-1.0, high=1.0, dtype=np.float64),
            "yaw"   : spaces.Box(low=-1.0, high=1.0, dtype=np.float64),
            "thrust": spaces.Box(low=-1.0, high=1.0, dtype=np.float64),
            "fire_machine_gun"  : spaces.Discrete(2)
        })

        self.observation_space = spaces.Dict({
            0 : init_observation(),
            1 : init_observation()
        })
        self.action_space = spaces.Dict({
            0 : init_action(),
            1 : init_action()
        })

        self.game_client = GameClient(
            server_ip,
            server_port,
            gladius_radius,
            enable_builtin_autopilot,
            enable_render = True if self.render_mode == "human" else False
        )
        self.game_client.connect()

    def reset(self, seed=None, options=None):
        print("resetting")
        super().reset(seed=seed)

        self.prev_observations = None
        self.plane_names = self.game_client.resetGame()
        self.plane_name_idx_map = {
            plane_name:idx for idx, plane_name in enumerate(self.plane_names)
        }
        raw_observations = self.game_client.calcObservation()
        observations = self.processRawObservation(raw_observations)
        return observations, raw_observations

    def step(self, control_action) :
        """
        Resets the environment to an initial state, required before calling step.
        Returns the first agent observation for an episode and information, i.e. metrics, debug info.
        """
        raw_observations, is_done = self.game_client.update(control_action)
        observations = self.processRawObservation(raw_observations)
        reward = self.calcReward(observations)

        #print(reward)

        return observations, reward, is_done, is_done, raw_observations

    def render(self):
        if self.render_mode == "rgb_array":
            pass
    
    def close(self):
        self.game_client.close()

    def processRawObservation(self, raw_observations) :
        observations = {}
        for plane_name, raw_obs in raw_observations.items() :
            obs = {}
            obs["dist_from_origin"] = raw_obs["dist_from_origin"]
            obs["health_level"]     = raw_obs["health_level"]
            obs["hit_count"]        = raw_obs["hit_count"]
            obs["num_bullet"]       = raw_obs["num_bullet"]
            obs["position"]         = raw_obs["position"]
            obs["rotation"]         = raw_obs["rotation"]
            obs["velocity"]         = raw_obs["velocity"]
            obs["velocity_norm"]    = raw_obs["velocity_norm"]
            obs["loose"] = False
            obs["won"] = False
            if raw_obs["health_level"] <= 1e-3 or raw_obs['destroyed'] or raw_obs['wreck'] :
                obs["loose"] = True
            if self.calcDistanceToBoundary(obs) <= 0 :
                obs["loose"] = True
            observations[self.plane_name_idx_map[plane_name]] = obs
        # assume only 2 aircraft in current development state
        for plane_idx, my_obs in observations.items() :
            for enemy_idx, enemy_obs in observations.items() :
                if enemy_idx == plane_idx :
                    continue
                vec_to_enemy = enemy_obs["position"] - my_obs["position"]
                vec_to_enemy_norm = vec_to_enemy / np.linalg.norm(vec_to_enemy)
                #my_direction = my_obs["velocity"] / np.linalg.norm(my_obs["velocity"])

                v_norm =  my_obs["velocity"] / np.linalg.norm(my_obs["velocity"])

                cos_angle_to_enemy = np.dot(vec_to_enemy_norm, obs["velocity_norm"])
                if plane_idx == 0 :
                    """
                    print(
                        "{:5d} {:5d}".format(
                            int(my_obs["dist_from_origin"]),
                            int(np.inner(my_obs['position'], my_obs["velocity"]))
                        )
                    )
                    """

                    format_str = "{:3d} {:4d}  " * 3
                    print(
                        format_str.format(
                            *np.array([
                                my_obs["velocity"],
                                my_obs["position"],
                            ]).transpose().reshape(-1).astype(np.int32)
                        )
                    )


                    """
                    format_str = "{:3.3f}  "*6
                    print(
                        format_str.format(
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[1, 2, 0]]),
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[0, 1, 2]]),
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[0, 2, 1]]),
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[1, 0, 2]]),
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[2, 0, 1]]),
                            np.inner(vec_to_enemy_norm, obs["velocity_norm"][[2, 1, 0]])
                        ),
                        #int(np.linalg.norm(vec_to_enemy)),
                    )
                    """

                observations[plane_idx]["angle_to_enemy"] = np.arccos(cos_angle_to_enemy)
                if enemy_obs["loose"] :
                    observations[plane_idx]["won"] = True
        return observations

    def calcReward(self, observations) :
        if not self.prev_observations :
            self.prev_observations = observations
            return 0

        rewards = {}
        for plane_idx, obs in observations.items() :
            reward = 0            
            prev_obs = self.prev_observations[plane_idx]

            num_bullet_fired = prev_obs["num_bullet"] - obs["num_bullet"]

            reward += obs["hit_count"] * 10000
            reward += num_bullet_fired * (10 / (obs["angle_to_enemy"] + 0.2))
            reward += num_bullet_fired * -15

            if plane_idx == 0 and  reward != 0 :
                print(int(obs["angle_to_enemy"] / np.pi * 180), reward)                

            # punish
            if obs["num_bullet"] == 0 :
                reward -= 1000

            reward += (prev_obs["health_level"] - obs["health_level"]) * -10000
            
            if obs["loose"] == True :
                reward -= -10000
            elif obs["won"] == True :
                reward += 10000
            
            reward -= (obs["dist_from_origin"] / self.gladius_radius) ** 3 * 1000
            rewards[plane_idx] = reward
            
            """
            print(
                "{} dist:{} fired:{} hit:{} gun_reward:{} health_diff:{} total:{}".format(
                    plane_name,
                    int(obs["dist_from_origin"]),
                    num_bullet_fired,
                    obs["hit_count"],
                    num_bullet_fired * obs["angle_to_enemy"]**3 - num_bullet_fired * -1,
                    prev_obs["health_level"] - obs["health_level"],
                    rewards[plane_name]
                ),
                end = "     "
            )
            """
        self.prev_observations = observations
        
        return rewards

    def calcDistanceToBoundary(self, observation) :
        """
        args
            pos : list
                [, height, ]
            orientation : list
                []

        return
            distance (along direction of plane) to wall.
            minus if out of boundary
        """

        position = observation["position"]
        velocity_norm = observation["velocity_norm"]

        if np.linalg.norm(position, ord = 2) >= self.gladius_radius :
            return -1
        else :
            return 1
        
        line_origin_distance = np.linalg.norm(np.outer(velocity_norm, position), ord = 2)
        base_length = np.sqrt(self.gladius_radius**2 - line_origin_distance**2)

        distance = base_length - np.dot(velocity_norm, position)

        #print("distance:", int(np.linalg.norm(position, ord = 2)), np.linalg.norm(velocity_norm))

        return distance


    def close(self):
        self.game_client.close()

if __name__ == "__main__" :
    pass