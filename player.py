import os
import sys
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
from data.globals.globals import *
from data.gameobjects.vector2 import Vector2


class Player():
    def __init__(self):
        self.type = 'player'

        self.entity_id = 0
        self.is_alive = True

        self.flip = False
        self.animation_list = animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3
        self.update_time = pygame.time.get_ticks()

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect(width=70, height=80)

        # image properties
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # hitbox
        self.hitbox_x_offset = 25
        self.hitbox_y_offset = 20

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        self.rect.center = -100, 100

        self.moving_left = False
        self.moving_right = True

        self.facing_positive = True
        # cooldowns
        self.cooldowns = {'melee': 2000, 'range': 2000}

        # attack damage
        self.shoot_damage = 200
        self.melee_damage = 180

        # speed
        self.speed = 250

        # projectiles
        self.projectiles = []

        # healthpoints
        self.health_points = 100
        self.max_health = 200

        self.states = {'IDLING': 'IDLING', 'RUNNING': 'RUNNING',
                       'ATTACKING': 'ATTACKING', 'FIRING': 'FIRING', 'DYING': 'DYING',
                       'HURTING': 'HURTING', 'RUNNING-FIRING': 'RUNNING-FIRING',
                       'RUNNING-ATTACKING': 'RUNNING-ATTACKING'}
        self.state = self.states['IDLING']

        self.init_state = True

    # update position

    def update(self, display, time, movement, entities):
        new_entities = new_list_without_self(self, entities)
        self.update_animation()

        if self.projectiles:
            for projectile in self.projectiles:
                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list):
                    for col in collision_list:
                        col.hit(projectile.damage)
                    self.projectiles.pop(
                        self.projectiles.index(projectile))

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER:
                    self.projectiles.pop(
                        self.projectiles.index(projectile))

                else:
                    projectile.update(time)

        if self.init_state:
            if self.facing_positive:
                self.flip = False
            else:
                self.flip = True

            if self.state == 'IDLING':
                self.set_action(Animation_type.Idle_Blinking)
            elif self.state == 'RUNNING':
                self.set_action(Animation_type.Running)
            elif self.state == 'HURTING':
                self.init_state = False
                self.set_action(Animation_type.Hurt)
            elif self.state == 'DYING':
                self.init_state = False
                self.set_action(Animation_type.Dying)
            elif self.state == 'RUNNING-ATTACKING':
                self.state_running_attacking(
                    display, new_entities)
            elif self.state == 'RUNNING-FIRING':
                self.state_running_firing(
                    display)
            elif self.state == 'ATTACKING':
                self.init_state = False
                self.set_action(Animation_type.Slashing)
                self.melee_attack(display, new_entities)
            elif self.state == 'FIRING':
                self.init_state = False
                self.set_action(Animation_type.Throwing_in_The_Air)
                self.fire(display)

        self.rect, collisions = self.move(
            self.rect, movement, new_entities, time)

    def move(self, rect, movement, new_entities, time):
        collision_types = {'top': False, 'bottom': False,
                           'left': False, 'right': False}

        self.rect.x += movement[0] * time * self.speed

        # collisions on x axis
        collision_list = check_collision(self.rect, new_entities)
        # we check if we collide with obstacle, first we check X axis coords, then y axis
        # this way we can correctly determine where the collision ocurred
        # for col in collision_list:
        #     if movement[0] > 0:
        #         # rect build in method allows us to set rect to side of another rect
        #         self.rect.right = col.hitbox.left
        #         collision_types['right'] = True
        #     elif movement[0] < 0:
        #         # rect build in method allows us to set rect to side of another rect
        #         self.rect.left = col.hitbox.right
        #         collision_types['left'] = True

        if self.rect.x + self.hitbox_x_offset < LEFT_BORDER:
            self.rect.x = LEFT_BORDER - self.hitbox_x_offset
        if(self.rect.x + self.rect.width + self.hitbox_x_offset > RIGHT_BORDER):
            self.rect.x = RIGHT_BORDER - self.rect.width - self.hitbox_x_offset
        self.hitbox.x = self.rect.x + self.hitbox_x_offset

        self.rect.y += movement[1] * time * self.speed

        # collisions on y axis
        collision_list = check_collision(self.rect, new_entities)
        # for col in collision_list:
        #     if movement[1] > 0:
        #         # rect build in method allows us to set rect to side of another rect
        #         self.rect.bottom = col.hitbox.top
        #         collision_types['bottom'] = True
        #     elif movement[1] < 0:
        #         # rect build in method allows us to set rect to side of another rect
        #         self.rect.top = col.hitbox.bottom
        #         collision_types['top'] = True

        if self.rect.y + self.image_height - self.hitbox_y_offset < TOP_BORDER:
            self.rect.y = TOP_BORDER - self.image_height + self.hitbox_y_offset
        if self.rect.y + self.image_height - self.hitbox_y_offset > BOTTOM_BORDER:
            self.rect.y = BOTTOM_BORDER - self.image_height + self.hitbox_y_offset
        self.hitbox.y = self.rect.y + self.hitbox_y_offset

        return self.rect, collision_types

    # draw player to canvas
    def draw(self, display, offset_x, offset_y, player):
        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))
        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.rect.width, self.rect.height], 2)

        pygame.draw.rect(display, (255, 122, 0), [
                         self.rect.x - offset_x, self.rect.y - offset_y, self.rect.width, self.rect.height], 2)

    def hit(self, damage):
        if self.is_alive:
            self.state = self.states['HURTING']
            self.health_points -= damage

    def update_animation(self):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Slashing) or self.action == int(Animation_type.Throwing_in_The_Air) or self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 30

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
            elif self.action == int(Animation_type.Slashing) or self.action == int(Animation_type.Throwing_in_The_Air):
                self.init_state = True
                self.state = self.states['IDLING']
            elif self.action == int(Animation_type.Run_Slashing) or self.action == int(Animation_type.Run_Throwing):
                self.init_state = True
                self.state = self.states['RUNNING']
            elif self.action == int(Animation_type.Hurt):
                self.init_state = True
                self.state = self.states['IDLING']
            else:
                self.frame_index = 0

    def set_action(self, new_action):
        # check if the new action != previous
        if int(new_action) != self.action:
            self.action = new_action
            # update animation from start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def melee_attack(self, display, new_entities):
        if self.facing_positive:
            direction = 1
        else:
            direction = -1
        attack = pygame.Rect(self.rect.x + (self.rect.w*direction), self.rect.y,
                             self.rect.width, self.rect.height)
        collision_list = check_collision(attack, new_entities)
        for col in collision_list:
            col.hit(self.melee_damage)

    def fire(self, display):
        if self.facing_positive:
            direction = 1
        else:
            direction = -1
        projectile = Projectile(
            Vector2(self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2), direction, Vector2(0, 0), 'player')
        self.projectiles.append(projectile)

    def state_running_attacking(self, display, new_entities):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Slashing)
            self.melee_attack(display, new_entities)

    def state_running_firing(self, display):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Throwing)
            self.fire(display)
