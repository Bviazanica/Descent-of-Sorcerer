import pygame
from pygame.locals import *

from data.gameobjects.vector2 import Vector2


class Enemy():
    def __init__(self):
        # image
        self.images = []
        self.enemy_img = pygame.image.load(
            'data/images/entities/enemy/woman.png').convert_alpha()
        self.images.append(self.enemy_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect(width=(70), height=(100))

        self.rect.x, self.rect.y = (400, 200)

        # hitbox
        self.hitbox = pygame.Rect(
            (self.rect.x + 10, self.rect.y + 35, 70, 100))

        # hp
        self.health_points = 100
        # borders

        # speed
        self.speed = 200

    def update(self, move, time, offset_x, offset_y):
        # self.rect = Vector2(
        #     self.rect.x, self.rect.y) + (move * time * self.speed)
        print("enemy update")

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))

        self.hitbox = pygame.Rect(
            (self.rect.x + 10 - offset_x, self.rect.y + 35 - offset_y, 70, 100))
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def hit(self):
        print("hit Sadge")
