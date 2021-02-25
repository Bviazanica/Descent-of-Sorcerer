import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2
import random


class Boss():
    def __init__(self):
        # image
        self.images = []
        self.boss_img = pygame.image.load(
            'data/images/entities/bosses/robot.png').convert_alpha()
        bossImg = pygame.transform.scale(self.boss_img, (72, 128))
        self.images.append(self.boss_img)
        self.image = self.images[0]

        # rect
        self.rect = self.image.get_rect(width=(75), height=(100))

        self.rect.x, self.rect.y = 200, 500
        # position
        self.position = 200, 500

        # hitbox
        self.hitbox = pygame.Rect(
            self.rect.x + 10, self.rect.y + 35, 75, 100)
        # speed
        self.speed = 200

        # healthpoints
        self.max_hp = 300
        self.health_points = 300

        self.hp_bar_width = self.rect.w

        # determine whether we render the entity
        self.visible = True

    def update(self, offset_x, offset_y):
        self.rect.x = self.position[0] - offset_x
        self.rect.y = self.position[1] - offset_y

        self.hitbox = pygame.Rect(
            self.rect.x + 10, self.rect.y + 35, 75, 100)

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))

        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

        # healthbar
        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox[0], self.hitbox[1] - 15, 75, 10))
        pygame.draw.rect(display, (0, 200, 0),
                         (self.hitbox[0], self.hitbox[1] - 15, self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)), 10))

    def hit(self, damage):
        self.health_points -= damage
