import numpy as np
import gymnasium as gym

from dogfight_env.envs import DogfightEnv

from xbox_cockpit import XboxCockpit


if __name__ == "__main__" :
    SERVER_IP = "192.168.219.104"
    SERVER_PORT = 50887

    xbox_cockpit = XboxCockpit()

    env = gym.make(
        "dogfight_env/DogfightEnv-v0",
        server_ip = SERVER_IP,
        server_port = SERVER_PORT,
        enable_builtin_autopilot = True,
        render_mode = "rgb_array"
    )
    env.reset()

    hit_count = 0

    while True :
        control_action = xbox_cockpit.update()
        
        observation, reward, done, done2, info = env.step(
            {
                env.plane_names[0] : control_action,
                #env.plane_names[1] : control_action
            }
        )
        
        if reward > 90 or reward < -90:
            print("reward :", reward)
        else :
            print("reward :", reward, end="\r")
        
        '''
        hit_flag = False
        for v in reward.values() :
            if v > 90 :
                hit_flag = True
                break
        if hit_flag :
            print("reward :", reward)
        else :
            print("reward :", reward, end="\r")
        '''


        ally_observation = info[env.plane_names[0]]
        ally_physics    = ally_observation["physics_parameters"]
        ally_position    = ally_observation["position"]
        ally_velocity    = ally_observation["move_vector"]
        ally_rotation    = ally_observation["Euler_angles"]
        world_speed      = ally_observation["world_speed"]
        enemy_observation = info[env.plane_names[1]]
        enemy_position    = enemy_observation["position"]

        env.render()
        if done :
            env.reset()
            print(".........................")