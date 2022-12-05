"""
import pygame
from pygame.locals import *

pygame.init()

joystick = pygame.joystick.Joystick(0)

while True:
    for event in pygame.event.get():
        # get the events (update the joystick)
        if event.type == QUIT:
            # allow to click on the X button to close the window
            pygame.quit()
            exit()

    if joystick.get_button(0):
        print("stopped")
        break

    print(type(event))
"""

import pygame
import sys

pygame.init()
pygame.joystick.init()
clock = pygame.time.Clock()

WIDTH,HEIGHT = 500,500
WHITE = (255,255,255)
BLUE = (0,0,255)
BLUISH = (75,75,255)
YELLOW =(255,255,0)
screen = pygame.display.set_mode((WIDTH,HEIGHT))

joysticks = [
    pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
]
    
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif  event.type == pygame.JOYBUTTONDOWN:
            if  event.button == 0: #press A button to smile
                screen.fill(WHITE)
                #screen.blit(smile,(0,0))
                pygame.display.update()
                clock.tick(10)
        elif  event.type == pygame.JOYBUTTONUP:
            if  event.button == 0:
                screen.fill(WHITE)
                #screen.blit(idle,(0,0))
                pygame.display.update()
                clock.tick(10)
