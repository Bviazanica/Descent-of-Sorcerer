import pygame
from pygame.locals import *

from data.gameobjects.vector2 import Vector2


class Projectile(object):
    def __init__(self, position, facing):
        self.images = []
        projectileImg = pygame.image.load(
            'data/images/projectiles/basic.png').convert_alpha()
        projectileImg = pygame.transform.scale(projectileImg, (20, 20))

        self.images.append(projectileImg)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.position = position
        self.rect.x, self.rect.y = self.position
        self.facing = facing
        self.speed = 10 * facing

    def update(self, offset_x, offset_y):
        self.rect.x += self.speed

        print(self.rect)

    def draw(self, display):
        display.blit(self.image, self.rect)
