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
        self.omegalul = 0.0
        self.rect.x, self.rect.y = 300, 300
        # hp
        self.health_points = 100
        # borders

        # speed
        self.speed = 200

    def update(self, move, time, offset_x, offset_y):
        # self.rect = Vector2(
        #     self.rect.x, self.rect.y) + (move * time * self.speed)
        self.rect.x, self.rect.y = 300 - offset_x, 300-offset_y

        print(self.rect)

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(display, (255, 0, 0), self.rect)