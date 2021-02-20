import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # image
        self.images = []
        bossImg = pygame.image.load(
            'data/images/entities/bosses/robot.png').convert_alpha()
        bossImg = pygame.transform.scale(bossImg, (72, 128))
        self.images.append(bossImg)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # hp
        self.health_points = 100
        # borders

        # speed
        self.speed = 200

        # healthpoints
        self.health_points = 300

    def update(self, move, time, offset_x, offset_y):
        # self.rect = Vector2(
        #     self.rect.x, self.rect.y) + (move * time * self.speed)
        self.rect.x, self.rect.y = 500 - offset_x, 500-offset_y

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x, self.rect.y))
