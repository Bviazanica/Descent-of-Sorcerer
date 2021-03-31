# Setup python
import os
import sys
import pygame
import random
from data import *
from data.utility import *
from pygame.locals import *
from data.globals.globals import *


class Button():
    def __init__(self, x, y, type):
        if type == 'menu':
            self.image = pygame.image.load(
                'data/images/button/new/button.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (200, 100))
            self.rect = self.image.get_rect(width=200, height=50)
            self.hitbox_y_offset = 25
        elif type == 'audio':
            self.image = pygame.image.load(
                'data/images/button/new/audio_on.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.hitbox_y_offset = 0
        else:
            self.image = pygame.image.load(
                'data/images/button/new/arrow.png').convert_alpha()
            self.rect = self.image.get_rect(width=50, height=50)
            self.hitbox_y_offset = 0
        self.rect.center = (x, y)
        self.clicked = False

        self.hitbox = pygame.Rect(
            (self.rect.x, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

    def draw(self, display):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.hitbox.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        display.blit(self.image, self.rect)
        return action
