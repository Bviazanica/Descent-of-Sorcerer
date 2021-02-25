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

        self.rect.x, self.rect.y = 400, 400
        # position
        self.position = 400, 400

        # hitbox
        self.hitbox = pygame.Rect(
            (self.rect.x + 10, self.rect.y + 35, 70, 100))

        # hp
        self.max_hp = 100
        self.health_points = 100

        self.hp_bar_width = self.rect.w
        # borders

        # speed
        self.speed = 200

    def update(self, offset_x, offset_y):

        self.rect.x = self.position[0] - offset_x
        self.rect.y = self.position[1] - offset_y

        self.hitbox = pygame.Rect(
            (self.rect.x + 10, self.rect.y + 35, 70, 100))

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox[0], self.hitbox[1] - 15, self.hp_bar_width, 10))
        pygame.draw.rect(display, (0, 200, 0),
                         (self.hitbox[0], self.hitbox[1] - 15, self.hp_bar_width - ((self.hp_bar_width/100)*(self.max_hp - self.health_points)), 10))

    def hit(self, damage):
        self.health_points -= damage
