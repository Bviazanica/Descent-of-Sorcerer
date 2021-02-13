import pygame
from pygame.locals import *

from data.gameobjects.vector2 import Vector2


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # image
        self.images = []
        spiderImg = pygame.image.load(
            'data/images/entities/enemy/woman.png').convert_alpha()
        self.images.append(spiderImg)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # hp
        self.health_points = 100
        # borders

        # position
        self.position = Vector2(400, 400)
        # speed
        self.speed = 200

    def update(self, offset_x, offset_y):
        # self.position = Vector2(
        #     self.rect.x - offset_y, self.rect.y - offset_y)
        # self.rect.x = self.position[0]
        # self.rect.y = self.position[1]
        self.rect.x = self.position[0] - offset_x
        self.rect.y = self.position[1] - offset_y

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))
