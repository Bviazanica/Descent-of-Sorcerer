import pygame
from pygame.locals import *

from data.gameobjects.vector2 import Vector2


class Projectile(object):
    def __init__(self, player_position, facing):
        self.images = []
        self.projectile_img = pygame.image.load(
            'data/images/projectiles/basic.png').convert_alpha()
        self.projectile_img = pygame.transform.scale(
            self.projectile_img, (5, 5))

        self.images.append(self.projectile_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        self.player_position = player_position
        self.change = 0
        self.rect.x = player_position[0]
        self.rect.y = player_position[1]

        self.hitbox = pygame.Rect(
            self.rect.x, self.rect.y, 5, 5)

        self.facing = facing
        self.speed = 250 * facing

    def update(self, x, y, time):
        self.rect.x = self.rect.x + (self.speed * time)

    def draw(self, display, offset_x, offset_y):
        self.hitbox = pygame.Rect(
            (self.rect.x - offset_x, self.rect.y-offset_y, 5, 5))
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y-offset_y))
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)
