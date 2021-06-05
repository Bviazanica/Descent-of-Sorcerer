import pygame
import random
from data.utility import *
from pygame.locals import *
from data.gameobjects.vector2 import Vector2

class Projectile(object):
    def __init__(self, position, direction, desired, projectile_id, damage, speed, projectiles_animation_list):
        # id
        self.projectile_id = projectile_id
        self.animation_list = projectiles_animation_list[self.projectile_id]

        self.frame_index = 0
        # load image depending on id of projectile
        if self.projectile_id:
            self.image = self.animation_list[self.frame_index]
        else:
            self.image_original = self.animation_list[0]
            self.image = self.image_original.copy()

        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

        self.update_time = 0
        self.animation_time = 0

        self.position = position
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.damage = damage

        self.desired = desired
        self.direction = direction
        self.speed = speed * self.direction
        if projectile_id and self.direction == 1:
            self.flip = True
        else:
            self.flip = False
        self.destroy = False
        self.collision = False
        # rotation of boss rocks
        self.rotation = 0
        self.rotation_speed = random.randrange(2, 10) * self.direction
        self.rotation_time = 0

    def update(self, time_passed, time, projectiles_list):
        self.update_time = time_passed
        if self.destroy:
            self.update_animation(projectiles_list)
        else:
            self.update_animation([])
            if self.projectile_id:
                self.rect.x += (self.speed * time)
            else:
                previous_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = previous_center

                self.position += self.desired * time * abs(self.speed)
                self.rect.center = self.position

    def draw(self, display, offset_x, offset_y):

        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

    # projectile animations
    def update_animation(self, projectiles_list):
        if self.projectile_id:
            ANIMATION_COOLDOWN = 30
            self.image = self.animation_list[self.frame_index]
        else:
            ANIMATION_COOLDOWN = 10
        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            if not self.projectile_id:
                self.rotation = (self.rotation + self.rotation_speed) % 360
                new_image = pygame.transform.rotate(
                    self.image_original, self.rotation)
                self.image = new_image
            self.frame_index += 1
        if not self.destroy and self.frame_index >= 4:
            self.frame_index = 0
        elif self.destroy and self.frame_index >= len(self.animation_list):
            projectiles_list.pop(projectiles_list.index(self))
