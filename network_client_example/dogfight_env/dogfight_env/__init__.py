from gymnasium.envs.registration import register

register(
    id = "dogfight_env/DogfightEnv-v0",
    entry_point="dogfight_env.envs:DogfightEnv",
)