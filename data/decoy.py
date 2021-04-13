import pygame
from data.utility import *
from pygame.locals import *
from data.gameobjects.vector2 import Vector2


class Decoy(object):
    def __init__(self, position, facing_positive, damage):
        self.type = 'decoy'
        self.is_alive = True
        # animations
        self.action = 3
        self.frame_index = 0
        self.animation_list = entities_animation_list[0]

        # local update time for animations
        self.update_time = 0

        self.animation_time = 0
        # image properties
        self.flip = False
        self.image = self.animation_list[self.action][self.frame_index]
        self.health_points = 200

        self.rect = self.image.get_rect(width=70, height=80)
        self.rect.topleft = position

        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

        self.hitbox_x_offset = 25
        self.hitbox_y_offset = 20
        self.facing_positive = facing_positive
        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        self.explosion_damage = damage
        self.states = {'IDLING': 'IDLING',
                       'HURTING': 'HURTING', 'EXPLODING': 'EXPLODING'}
        self.state = self.states['IDLING']
        self.dying_position = Vector2(0, 0)
        self.init_state = True
        self.ready_to_explode = False

        check_boundaries_for_x(self)
        check_boundaries_for_y(self)

    def update(self, time_passed, new_entities):
        self.update_time = time_passed
        self.update_animation(new_entities)
        if self.is_alive:
            if self.init_state:
                if self.state == 'IDLING':
                    self.set_action(Animation_type.Idle_Blinking)
                elif self.state == 'HURTING':
                    self.init_state = False
                    self.set_action(Animation_type.Hurt)

        if self.state == self.states['EXPLODING']:
            self.rect = self.image.get_rect()
            self.rect.centerx = self.dying_position[0]
            self.rect.bottom = self.dying_position[1]

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, not self.facing_positive, False), (self.rect.x -
                                                                                          offset_x, self.rect.y - offset_y))

    def hit(self, damage):
        if self.state != self.states['EXPLODING']:
            if self.health_points - damage <= 0:
                self.is_alive = False
                self.health_points = 0
                self.init_state = False
                self.state = self.states['EXPLODING']
                self.set_action(Animation_type.Exploding)
                self.ready_to_explode = True
                self.dying_position = Vector2(
                    self.hitbox.centerx, self.hitbox.bottom)
            elif self.is_alive and self.state == self.states['HURTING']:
                self.frame_index = 0
                self.init_state = False
                self.health_points -= damage
                hit_sound.play()
            elif self.is_alive:
                self.frame_index = 0
                self.set_action(Animation_type.Hurt)
                self.state = self.states['HURTING']
                self.init_state = False
                self.health_points -= damage
                hit_sound.play()

    def update_animation(self, new_entities):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        if self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 15

        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1
        if self.frame_index == 3 and self.action == int(Animation_type.Exploding) and self.ready_to_explode:
            explode_sound.play()
            self.ready_to_explode = False
            collision_list = check_collision(self.rect, new_entities)
            if len(collision_list):
                for col in collision_list:
                    if col.type == 'player' or col.type == 'decoy' or col.state != col.states['APPEARING']:

                        col.hit(self.explosion_damage)
        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Hurt):
                self.init_state = True
                self.state = self.states['IDLING']
            elif self.action == int(Animation_type.Exploding):
                self.init_state = True
            else:
                self.frame_index = 0

    def set_action(self, new_action):
        # check if the new action != previous
        if int(new_action) != self.action:
            self.action = new_action
            # update animation from start
            self.frame_index = 0
            self.animation_time = self.update_time
