import pygame
from utility import *
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Projectile(object):
    def __init__(self, position, direction, desired, projectile_id, damage):

        # id
        self.projectile_id = projectile_id
        self.animation_list = projectiles_animation_list[self.projectile_id]

        self.frame_index = 0
        # load image depending on id of projectile
        if self.projectile_id:
            self.image = self.animation_list[self.frame_index]
        else:
            self.image = self.animation_list[0]
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

        self.update_time = 0
        self.animation_time = 0

        self.position = position
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.hitbox_x_offset = 30
        self.hitbox_y_offset = 5
        self.hitbox = pygame.Rect(
            self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.image_width, self.image_height)

        self.damage = damage

        self.desired = desired
        self.direction = direction
        self.speed = 400 * self.direction
        if projectile_id and self.direction == 1:
            self.flip = True
        else:
            self.flip = False

    def update(self, time_passed, time, projectiles_list, destroy):
        self.update_time = time_passed
        if destroy:
            self.update_animation(projectiles_list, destroy)
            self.damage = 0
        else:
            self.update_animation([], False)
            if self.projectile_id:
                self.rect.x += (self.speed * time)
            else:
                self.position += self.desired * time * self.speed
                self.rect.center = self.position

            self.hitbox[0] = self.rect.x + self.hitbox_x_offset
            self.hitbox[1] = self.rect.y + self.hitbox_y_offset

    def draw(self, display, offset_x, offset_y):
        pygame.draw.rect(display, RED, [
                         self.rect.x - offset_x, self.rect.y - offset_y, self.rect.w, self.rect.h], 2)
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

    def update_animation(self, projectiles_list, destroy):
        ANIMATION_COOLDOWN = 10
        if self.projectile_id:
            self.image = self.animation_list[self.frame_index]
        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1
        if not destroy and self.frame_index >= 4:
            self.frame_index = 0
        elif destroy and self.frame_index >= len(self.animation_list):
            projectiles_list.pop(projectiles_list.index(self))
