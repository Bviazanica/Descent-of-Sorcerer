import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Boss():
    def __init__(self):
        # image
        self.images = []
        self.boss_img = pygame.image.load(
            'data/images/entities/bosses/robot.png').convert_alpha()
        bossImg = pygame.transform.scale(self.boss_img, (72, 128))
        self.images.append(self.boss_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # hp
        self.health_points = 100

        self.rect.x, self.rect.y = (200, 400)

        # hitbox
        self.hitbox = pygame.Rect(
            self.rect.x + 10, self.rect.y + 35, 75, 100)
        # speed
        self.speed = 200

        # healthpoints
        self.health_points = 300

    def update(self, move, time, offset_x, offset_y):
        # self.rect = Vector2(
        #     self.rect.x, self.rect.y) + (move * time * self.speed)
        print("boss update")

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))

        self.hitbox = pygame.Rect(
            self.rect.x - offset_x + 10, self.rect.y + 35 - offset_y, 75, 100)
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def hit(self):
        print("hit Sadge")
