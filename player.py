import os
import sys
import pygame
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Player():
    def __init__(self):
        self.images = []
        self.player_img = pygame.image.load(
            'data/images/entities/hero/hero.png').convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (36, 64))
        self.images.append(self.player_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        # hitbox
        self.hitbox = pygame.Rect(
            self.rect.x, self.rect.y, self.player_img.get_width(), self.player_img.get_height())
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
    def update(self, display, time, movement, obstacles, offset_x, offset_y):
        self.rect, self.collisions = self.move(
            self.rect, movement, obstacles, time)

    def check_collision(self, rect, obj_list):
        self.collisions = []
        for obj in obj_list:
            if self.rect.colliderect(obj):
                self.collisions.append(obj)
        return self.collisions

    def move(self, rect, movement, obstacles, time):
        self.collision_types = {'top': False, 'bottom': False,
                                'left': False, 'right': False}

        self.rect.x += movement[0] * time * self.speed
        # collisions on x axis
        self.collision_list = self.check_collision(self.rect, obstacles)
        # we check if we collide with obstacle, first we check X axis coords, then y axis
        # this way we can correctly determine where the collision ocurred
        for col in self.collision_list:
            if movement[0] > 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.right = col.left
                self.collision_types['right'] = True
            elif movement[0] < 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.left = col.right
                self.collision_types['left'] = True
        if(self.rect.x < self.left_border):
            self.rect.x = self.left_border
        if(self.rect.x > self.right_border - self.rect.width):
            self.rect.x = self.right_border - self.rect.width
        self.rect.y += movement[1] * time * self.speed
        # collisions on y axis
        self.collision_list = self.check_collision(self.rect, obstacles)
        for col in self.collision_list:
            if movement[1] > 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.bottom = col.top
                self.collision_types['bottom'] = True
            elif movement[1] < 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.top = col.bottom
                self.collision_types['top'] = True

        if(self.rect.y < self.player_border_min_y):
            self.rect.y = self.player_border_min_y
        if(self.rect.y > self.player_border_max_y - self.rect.height):
            self.rect.y = self.player_border_max_y - self.rect.height
        return self.rect, self.collision_types

    # draw player to canvas

    def draw(self, display, offset_x, offset_y):
        display.blit(
            self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

        self.hitbox = pygame.Rect(
            self.rect.x - offset_x, self.rect.y - offset_y, self.player_img.get_width(), self.player_img.get_height())
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)
    # basic attack

    def fire(self):
        print("attacking!")
