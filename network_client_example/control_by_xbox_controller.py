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
    SERVER_IP = "192.168.219.108"
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

        
        # get angle between ally velocity and vector from ally to enemy
        angle_to_enemy = np.arccos(
            np.dot(
                ally_velocity, relative_position
            ) / (
                np.linalg.norm(ally_velocity) * np.linalg.norm(relative_position)
            )
        )
        
        distance = np.linalg.norm(relative_position, ord = 2)

        print("angle :", f"{str(np.rad2deg(angle_to_enemy))}",  "distance", distance)

        #print("p", ally_position) #, "v", ally_velocity, "a", ally_euler_angle)
        #print("angle", ally_euler_angle)
        

        #print("target_id", observation["target_id"], obs_enemy["target_id"])
        #print(observation["cos_angle_to_enemy"])
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
            
