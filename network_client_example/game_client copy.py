import pygame
import dogfight_client as df
import time
import sys
import numpy as np

class GameClient :
    def __init__(self, server_ip, server_port) :

        df.connect(server_ip, server_port)
        time.sleep(2) 
        df.disable_log()

        self.planes = df.get_planes_list()
        self.user_plane_idx = 0

        df.set_client_update_mode(True)

        self.prev_observations = None

    def resetGame(self) :
        pass

    def pauseGame(self) :
        pass    

    def close(self) :
        df.set_client_update_mode(False)
        df.disconnect()

    def update(self, control_actions:dict) :
        # put control actions to plane
        for plane_name, control_action in control_actions.items() :

            df.set_plane_roll(plane_name, control_action["roll"])
            df.set_plane_pitch(plane_name, control_action["pitch"])
            df.set_plane_yaw(plane_name, control_action["yaw"])
            df.set_plane_thrust(plane_name, control_action["thrust"])
            
            if control_action["fire_machine_gun"] :
                df.fire_machine_gun(plane_name)
            else :
                df.cease_machine_gun(plane_name)
        df.update_scene()

        observations = self.caclObservation()
        rewards = self.calcReward(observations)
        is_done = self.checkEpisodEnd(observations)

        if is_done :
            pass

        return observations, rewards, is_done

    def caclObservation(self) :
        observations = {}
        for plane_name in self.planes :
            observations[plane_name] = df.get_plane_state(plane_name)

    def isInGladius(self, pos) :
        pass

    def distanceToBoundary(self, pos:list, orientation:list) :
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
        return 

    def checkEpisodEnd(self, observations) :
        for plane, obs in observations.items() :
            if obs["health_level"] == 0 :
                return True
            if obs['destroyed'] or ['wreck'] or ['crashed'] :
                return True
            if self.distanceToBoundary(obs["position"], obs["Euler_angles"]) <= 0 :
                return True

        return False
        
        
    def calcReward(self, observations) :
        if not self.prev_observations :
            self.prev_observations = observations
            return 0

        rewards = {}
        for plane_name, obs in observations.items() :
            reward = 0            
            prev_obs = self.prev_obs[plane_name]

            reward -= prev_obs["health_level"] - obs["health_level"] * 100
            if obs["health_level"] == 0 :
                reward -= 10000
            if obs['destroyed'] :
                reward -= 10000
            if ['wreck'] :
                reward -= 10000
            if self.distanceToBoundary(obs["position"], obs["Euler_angles"]) <= 0 :
                reward -= 10000

            rewards[plane_name] = reward



        


if __name__ == "__main__":
    
    SERVER_IP = "192.168.219.101"
    SERVER_PORT = 50888
    
    game_client = GameClient(SERVER_IP, SERVER_PORT)
    
    while True :
        pass