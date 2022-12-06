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
    game_client = GameClient(SERVER_IP, SERVER_PORT)
    
    while True :
        control_action = xbox_cockpit.update()
        game_client.step()