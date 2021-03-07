import os
import sys
import pygame
from pygame.locals import *
from entity import *
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

        # cooldowns
        self.cooldowns = {'melee': 2000, 'shoot': 2000}

        # attack damage
        self.shoot_damage = 10
        self.melee_damage = 25

        # speed
        self.speed = 250

        # healthpoints
        self.health_points = 100

        # camera borders
        self.top_border, self.bottom_border = -268, 746
        self.left_border, self.right_border = -380, 1500
        self.player_border_min_y, self.player_border_max_y = 120, 640

    # update position

    def update(self, display, time, movement, obstacles, offset_x, offset_y):
        self.rect, collisions = self.move(
            self.rect, movement, obstacles, time)

        print(collisions)

    def move(self, rect, movement, obstacles, time):
        collision_types = {'top': False, 'bottom': False,
                           'left': False, 'right': False}

        self.rect.x += movement[0] * time * self.speed
        # collisions on x axis
        collision_list = check_collision(self.rect, obstacles)
        # we check if we collide with obstacle, first we check X axis coords, then y axis
        # this way we can correctly determine where the collision ocurred
        for col in collision_list:
            if movement[0] > 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.right = col.hitbox.left
                collision_types['right'] = True
            elif movement[0] < 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.left = col.hitbox.right
                collision_types['left'] = True

        if(self.rect.x < self.left_border):
            self.rect.x = self.left_border
        if(self.rect.x > self.right_border - self.rect.width):
            self.rect.x = self.right_border - self.rect.width

        self.rect.y += movement[1] * time * self.speed
        # collisions on y axis
        collision_list = check_collision(self.rect, obstacles)
        for col in collision_list:
            if movement[1] > 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.bottom = col.hitbox.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                # rect build in method allows us to set rect to side of another rect
                self.rect.top = col.hitbox.bottom
                collision_types['top'] = True

        if(self.rect.y < self.player_border_min_y):
            self.rect.y = self.player_border_min_y
        if(self.rect.y > self.player_border_max_y - self.rect.height):
            self.rect.y = self.player_border_max_y - self.rect.height

        return self.rect, collision_types

    # draw player to canvas
    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))
        self.hitbox = pygame.Rect(
            (self.rect.x - offset_x, self.rect.y - offset_y, self.player_img.get_width(), self.player_img.get_height()))
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def fire(self):
        self.cooldown = True
        print("attacking!")
    # basic attack

    def melee_attack(self, display, obstacles, offset_x, offset_y):
        if self.right:
            direction = 1
        else:
            direction = -1
        attack = pygame.Rect(self.rect.x + (self.rect.w*direction), self.rect.y,
                             36, 64)

        collision_list = check_collision(attack, obstacles)
        for col in collision_list:
            print(col)
            col.hit(self.melee_damage)
