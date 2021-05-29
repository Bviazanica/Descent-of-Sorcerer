import random
import pygame
from data.utility import *
from pygame.locals import *
from data.projectile import Projectile
Vector2 = pygame.math.Vector2


class Item():
    def __init__(self, name, pos, w, h):
        self.name = name
        item_image = pygame.image.load(
            f'data/images/items/{name}_potion.png').convert_alpha()
        self.image = pygame.transform.smoothscale(item_image, (w, h))

        self.rect = self.image.get_rect()

        self.rect.center = pos
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, w, h)
        self.position = pos

    def update(self):
        pass

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))
