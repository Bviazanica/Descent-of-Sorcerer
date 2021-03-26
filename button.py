# Setup python
import os
import sys
import pygame
import random
from data import *
from utility import *
from pygame.locals import *
from data.globals.globals import *


class Button():
    def __init__(self, x, y, type):
        if type == 'menu':
            self.image = pygame.image.load(
                'data/images/button/new/button.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (200, 100))
        else:
            self.image = pygame.image.load(
                'data/images/button/new/arrow.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False

    def draw(self, display):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        display.blit(self.image, self.rect)

        return action
