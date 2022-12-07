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
        self.render_mode = render_mode

        self.observation_space = spaces.Dict({
            0 : spaces.Dict({
                "position"          : spaces.Box(np.float32([-gladius_radius]*3), np.float32([gladius_radius]*3), shape=(3,), dtype=np.float32),
                "rotation"          : spaces.Box(np.float32([-180]*3), np.float32([180]*3), shape=(3,), dtype=np.float32),
                "Euler_angles"      : spaces.Box(np.float32([-2*np.pi]*3), np.float32([2*np.pi]*3), shape=(3,), dtype=np.float32),
                "velocity"          : spaces.Box(np.float32([-2000]*3), np.float32([2000]*3), shape=(3,), dtype=np.float32),
                "velocity_norm"     : spaces.Box(np.float32([-1]*3), np.float32([1]*3), shape=(3,), dtype=np.float32),
                "dist_from_origin"  : spaces.Box(np.float32([0]), np.float32([gladius_radius]), dtype=np.float32),
                "angle_to_enemy"    : spaces.Box(np.float32([-np.pi]), np.float32([np.pi]), dtype=np.float32),
                "num_bullet"        : spaces.Box(0, 100000, dtype=np.uint32),
                "hit_count"         : spaces.Box(0, 255, dtype=np.uint8),
                "health_level"      : spaces.Box(np.float32([0]), np.float32([1]), dtype=np.float32),
                "loose"             : spaces.Discrete(2),
                "won"               : spaces.Discrete(2)
            }),
            1 : spaces.Dict({
                "position"          : spaces.Box(np.float32([-gladius_radius]*3), np.float32([gladius_radius]*3), shape=(3,), dtype=np.float32),
                "rotation"          : spaces.Box(np.float32([-180]*3), np.float32([180]*3), shape=(3,), dtype=np.float32),
                "Euler_angles"      : spaces.Box(np.float32([-2*np.pi]*3), np.float32([2*np.pi]*3), shape=(3,), dtype=np.float32),
                "velocity"          : spaces.Box(np.float32([-2000]*3), np.float32([2000]*3), shape=(3,), dtype=np.float32),
                "velocity_norm"     : spaces.Box(np.float32([-1]*3), np.float32([1]*3), shape=(3,), dtype=np.float32),
                "dist_from_origin"  : spaces.Box(np.float32([0]), np.float32([gladius_radius]), dtype=np.float32),
                "angle_to_enemy"    : spaces.Box(np.float32([-np.pi]), np.float32([np.pi]), dtype=np.float32),
                "num_bullet"        : spaces.Box(0, 100000, dtype=np.uint32),
                "hit_count"         : spaces.Box(0, 255, dtype=np.uint8),
                "health_level"      : spaces.Box(np.float32([0]), np.float32([1]), dtype=np.float32),
                "loose"             : spaces.Discrete(2),
                "won"               : spaces.Discrete(2)
            })
        })

        self.action_space = spaces.Dict({
            0 : spaces.Dict({    
                "roll"  : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "pitch" : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "yaw"   : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "thrust": spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "fire_machine_gun"  : spaces.Discrete(2)
            }),
            1 : spaces.Dict({    
                "roll"  : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "pitch" : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "yaw"   : spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "thrust": spaces.Box(low=-1.0, high=1.0, dtype=np.float32),
                "fire_machine_gun"  : spaces.Discrete(2)
            })
        })

        self.game_client = GameClient(
            server_ip,
            server_port,
            gladius_radius,
            enable_builtin_autopilot
        )
        self.game_client.connect()

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        self.plane_names = self.game_client.resetGame()
        observation, is_done = self.game_client.calcObservation()
        info = None

        print(type(observation))
        print(observation)

        return observation, info

    def step(self, control_action) :
        observations, is_done = self.game_client.update(control_action)
        reward = self.game_client.calcReward(observations)

        return observations, reward, is_done, False, None

    def render(self):
        if self.render_mode == "rgb_array":
            pass

    def processObservation(self, observations) :
        pass

    def close(self):
        self.game_client.close()

if __name__ == "__main__" :
    pass