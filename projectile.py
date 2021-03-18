import pygame
from utility import *
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Projectile(object):
    def __init__(self, position, direction, desired, projectile_type):
        self.images = []
        self.projectile_img = pygame.image.load(
            'data/images/projectiles/basic.png').convert_alpha()
        self.projectile_img = pygame.transform.scale(
            self.projectile_img, (20, 20))

        self.images.append(self.projectile_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        self.position = position

        self.rect.center = self.position

        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, 20, 20)

        self.damage = 10

        self.type = projectile_type

        self.desired = desired
        self.speed = 100 * direction

    def update(self, time):
        if self.type == 'player':
            self.damage = 50
            self.rect.x += (self.speed * time)
        elif self.type == 'boss':
            self.damage = 20
            self.position += self.desired * time * self.speed
            self.rect.center = self.position

        self.hitbox[0] = self.rect.x
        self.hitbox[1] = self.rect.y

    def draw(self, display, offset_x, offset_y):
        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox[0] - offset_x, self.hitbox[1] - offset_y, 20, 20], 2)
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y-offset_y))
