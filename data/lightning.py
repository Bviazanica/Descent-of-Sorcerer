import pygame
from data.utility import *
from pygame.locals import *


class Lightning():
    def __init__(self, pos, name, spell_id, direction, offset):
        self.name = name
        self.spell_id = spell_id
        self.animation_list = spells_animation_list[self.spell_id]
        self.frame_index = 0

        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.hitbox_x_offset, self.hitbox_y_offset = offset

        self.update_time = self.animation_time = 0
        self.ready = False
        self.damage = 60
        if direction == 1:
            self.hitbox = pygame.Rect(
                self.rect.x + self.hitbox_x_offset, self.rect.y+self.rect.height-self.hitbox_y_offset, 180, 100)
            self.flip = True
        else:
            self.hitbox = pygame.Rect(
                self.rect.x, self.rect.y+self.rect.height-self.hitbox_y_offset,  180, 100)
            self.flip = False

    def update(self, time_passed, lightnings_list, new_entities):
        self.update_time = time_passed
        self.update_animation(lightnings_list, new_entities)

    def draw(self, display, offset_x, offset_y):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.hitbox.width, self.hitbox.height], 2)

    def update_animation(self, lightnings_list, new_entities):
        ANIMATION_COOLDOWN = 50
        self.image = self.animation_list[self.frame_index]

        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1
        if self.frame_index == 5 and self.ready:
            collision_list = check_collision(self.hitbox, new_entities)
            if len(collision_list):
                for col in collision_list:
                    col.hit(self.damage)
            self.ready = False
        if self.frame_index >= len(self.animation_list):
            lightnings_list.pop(lightnings_list.index(self))
