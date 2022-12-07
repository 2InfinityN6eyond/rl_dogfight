import pygame
import dogfight_client as df
import time
import sys
import numpy as np

from game_client import GameClient
from xbox_cockpit import XboxCockpit


if __name__ == "__main__":
    
    SERVER_IP = "192.168.219.101"
    SERVER_PORT = 50888

    xbox_cockpit = XboxCockpit()
    game_client = GameClient(SERVER_IP, SERVER_PORT, enable_autopilot=True)
    game_client.connect()
    plane_names = game_client.resetGame()
    user_plane_name = plane_names[0]

    prev_time_stamp = time.time()

    while True :

        control_action = xbox_cockpit.update()
        observations, is_done = game_client.update({
            plane_name : control_action for plane_name in plane_names
        })
 
        """
        observation = observations[user_plane_name]
        distance = game_client.distanceToBoundary(observation)

        position    = observation["position"]
        euler_angle = observation["Euler_angles"]
        hspeed      = observation["horizontal_speed"]
        vspeed      = observation["vertical_speed"]
        velocity    = observation["move_vector"]

        obs_enemy = observations[plane_names[-1]]
        """

        #print("target_id", observation["target_id"], obs_enemy["target_id"])
        #print(observation["cos_angle_to_ennemy"])
        """
        if observation["hit_count"] :
            print( "num_bullet", observation["num_bullet"], "hit :", observation["hit_count"])
        """

        """
        time_stamp = time.time()
        print(observation["timestep"], time_stamp - prev_time_stamp, end = " ")

        prev_time_stamp = time_stamp

        print(
            "p:{} an:{} v:{} nv:{}".format(
                np.array(position).astype(np.int32),
                (np.array(euler_angle) * 180 / np.pi).astype(np.int32),
                np.array(velocity).astype(np.int32),
                np.array(velocity) / np.linalg.norm(np.array(velocity))
            ),
            end = "      "
        )

        print(int(np.linalg.norm(np.array(position), ord = 2)), int(distance))
        """
        """"""

        if is_done :
            print("episode end")
            time.sleep(5)
            plane_names = game_client.resetGame()
            user_plane_name = plane_names[0]
            
