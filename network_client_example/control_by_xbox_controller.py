import pygame
import dogfight_client as df
import time
import sys
import numpy as np

from game_client import GameClient
from xbox_cockpit import XboxCockpit


if __name__ == "__main__":
    
    SERVER_IP = "192.168.219.105"
    SERVER_IP = "192.168.219.100"
    SERVER_IP = "172.26.224.1"
    SERVER_IP = "192.168.219.108"
    SERVER_IP = "192.168.219.108"
    SERVER_IP = "192.168.219.108"
    SERVER_IP = "192.168.219.104"
    SERVER_PORT = 50888

    xbox_cockpit = XboxCockpit()
    game_client = GameClient(
        SERVER_IP,
        SERVER_PORT,
        enable_autopilot=True,
        enable_render=False
    )
    
    game_client.connect()
    plane_names = game_client.resetGame()
    user_plane_name = plane_names[0]

    prev_time_stamp = time.time()

    i = 0
    while True :

        control_action = xbox_cockpit.update()




        observations, is_done = game_client.update({
            plane_name : control_action for plane_name in plane_names
        })
 



        ally_observation = observations[user_plane_name]
        #distance = game_client.distanceToBoundary(observation)

        ally_position    = ally_observation["position"]
        ally_euler_angle = ally_observation["Euler_angles"]
        ally_hspeed      = ally_observation["horizontal_speed"]
        ally_vspeed      = ally_observation["vertical_speed"]
        ally_velocity    = ally_observation["move_vector"]

        enemy_observation = observations[plane_names[-1]]

        enemy_position    = enemy_observation["position"]
        enemy_euler_angle = enemy_observation["Euler_angles"]
        enemy_hspeed      = enemy_observation["horizontal_speed"]
        enemy_vspeed      = enemy_observation["vertical_speed"] 
        enemy_velocity    = enemy_observation["move_vector"]
        



        relative_position = np.array(enemy_position) - np.array(ally_position)

        t_dir = relative_position / np.linalg.norm(relative_position)
        dir = np.array(ally_observation["aZ"])

        target_angle = np.arccos(np.dot(t_dir, dir) / (np.linalg.norm(t_dir) * np.linalg.norm(dir)))   
    

        print(
            "target_angle: ", int(target_angle * 180 / np.pi),
            np.dot(dir / np.linalg.norm(dir), ally_velocity / np.linalg.norm(ally_velocity)),
        )
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
            time.sleep(1)
            plane_names = game_client.resetGame()
            user_plane_name = plane_names[0]
            
