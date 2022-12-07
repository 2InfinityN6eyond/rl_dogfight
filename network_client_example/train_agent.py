import gymnasium as gym
#from dogfight_env.dogfight_env.envs.dogfight_env import DogfightEnv

from dogfight_env.envs import DogfightEnv

import pygame
#import dogfight_client as df
import time
import sys
import numpy as np

#from game_client import GameClient
from xbox_cockpit import XboxCockpit


if __name__ == "__main__" :

    SERVER_IP = "192.168.219.101"
    SERVER_PORT = 50888
    
    """
    env = gym.make(
        "dogfight_env:DogfightEnv-v0",
        server_ip = SERVER_IP,
        server_port = SERVER_PORT,
        enable_builtin_autopilot = True
    )
    """
    env = gym.make(
        "dogfight_env/DogfightEnv-v0",
        server_ip = SERVER_IP,
        server_port = SERVER_PORT,
        enable_builtin_autopilot = True
    )

    xbox_cockpit = XboxCockpit()

    observation, info = env.reset()

    plane_names = env.plane_names

    while True :
        control_action = xbox_cockpit.update()
        observation, reward, terminated, truncated, info = env.step({
            plane_name:control_action for plane_name in plane_names
        })

        if terminated :
            observation, info = env.reset()