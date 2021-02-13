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

        # position
        self.position = Vector2(500, 400)

        # speed
        self.speed = 200

    def update(self, offset_x, offset_y):
        self.rect.x = self.position[0] - offset_x
        self.rect.y = self.position[1] - offset_y

    def draw(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))
