import os
import sys
import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        playerImg = pygame.image.load(
            'data/images/entities/hero/hero.png').convert_alpha()
        playerImg = pygame.transform.scale(playerImg, (36, 64))
        self.images.append(playerImg)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.playerImgWidth = playerImg.get_width()
        self.playerImgHeight = playerImg.get_height()
        self.player_pos = Vector2(0, 0)
        self.player_speed = 200

    def update(self, move, time):
        self.player_pos = Vector2(
            self.rect.x, self.rect.y) + (move * time * self.player_speed)
        self.rect.x = self.player_pos[0]
        self.rect.y = self.player_pos[1]
