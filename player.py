import os
import sys
import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        self.player_img = pygame.image.load(
            'data/images/entities/hero/hero.png').convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (36, 64))
        self.images.append(self.player_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        # direction
        self.left = False
        self.right = True

        # speed & position
        self.speed = 250

        # healthpoints
        self.health_points = 100

        # camera borders
        self.top_border, self.bottom_border = -268, 746
        self.left_border, self.right_border = -380, 1500
        self.player_border_min_y, self.player_border_max_y = 120, 640

    # update position
    def update(self, move, time, offset_x, offset_y):
        pygame.sprite.Sprite.update(self)
        self.position = Vector2(
            self.rect.x, self.rect.y) + (move * time * self.speed)
        if(self.position[0] < self.left_border):
            self.position[0] = self.left_border
        if(self.position[0] > self.right_border - self.rect.width):
            self.position[0] = self.right_border - self.rect.width
        if(self.position[1] < self.player_border_min_y):
            self.position[1] = self.player_border_min_y
        if(self.position[1] > self.player_border_max_y - self.rect.height):
            self.position[1] = self.player_border_max_y - self.rect.height

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
    # drive player to canvas

    def draw(self, display, offset_x, offset_y):
        display.blit(
            self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
        self.hitbox = pygame.Rect(self.rect.x - offset_x,
                                  self.rect.y - offset_y, self.player_img.get_width(), self.player_img.get_height())

        pygame.draw.rect(display, (255, 0, 0), self.hitbox)
    # basic attack

    def attack(self):
        print("attacking!")
