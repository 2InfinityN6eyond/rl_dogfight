import gymnasium as gym

from dogfight_env.envs import DogfightEnv

from xbox_cockpit import XboxCockpit


if __name__ == "__main__" :
    SERVER_IP = "192.168.219.108"
    SERVER_PORT = 50888

    xbox_cockpit = XboxCockpit()

    env = gym.make(
        "dogfight_env/DogfightEnv-v0",
        server_ip = SERVER_IP,
        server_port = SERVER_PORT,
        enable_builtin_autopilot = True
    )
    env.reset()

    while True :
        control_action = xbox_cockpit.update()
        observation, reward, done, done2, info = env.step(
            {env.plane_names[0] : control_action}
        )
        env.render()
        if done :
            env.reset()