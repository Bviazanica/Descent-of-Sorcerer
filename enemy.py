import math
import pygame
from utility import *
from random import randint
from pygame.locals import *
from data.globals.globals import *
Vector2 = pygame.math.Vector2


class Enemy():
    def __init__(self, x, y):
        self.type = 'mob'

        self.entity_id = 2
        self.is_alive = True

        self.flip = False
        self.animation_list = animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3
        self.update_time = pygame.time.get_ticks()

        self.image = self.animation_list[self.action][self.frame_index]
        # rect
        self.rect = self.image.get_rect(width=55, height=70)

        self.rect.x, self.rect.y = (x, y)

        # image properties
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # hitbox
        self.hitbox_x_offset = 30
        self.hitbox_y_offset = 15

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))
        # hp
        self.max_hp = 200
        self.health_points = 200

        self.hp_bar_width = self.rect.w

        # speed
        self.speed = 200
        self.acceleration = Vector2(0, 0)

        # attack damage
        self.damage = 5

        # how fast the acceleration vector follows desired vec
        self.max_force = 0.08
        self.approach_radius = 120
        # states
        self.states = {'SEEKING': 'SEEKING', 'HUNTING': 'HUNTING',
                       'FLEE': 'FLEE', 'SACRIFICE': 'SACRIFICE',
                       'HURTING': 'HURTING', 'DYING': 'DYING',
                       'ATTACKING': 'ATTACKING', 'IDLING': 'IDLING'}

        self.state = self.states['SEEKING']

        self.last_state = ''
        self.init_state = True

        self.timer = 0

        self.desired = Vector2(0, 0)

        self.vector1 = Vector2(0, 0)
        self.vector2 = Vector2(0, 0)
        self.vector3 = Vector2(0, 0)
        self.vector4 = Vector2(0, 0)

    def update(self, time, player, current_time, mobs):
        self.update_animation()

        if self.is_alive:
            if self.desired[0] <= 0:
                self.flip = True
            else:
                self.flip = False

            if self.state == 'SEEKING':
                self.acceleration += self.state_seeking(
                    time, player, current_time, mobs)
            elif self.state == 'HUNTING':
                self.acceleration += self.state_hunting(
                    time, player, current_time, mobs)
            elif self.state == 'FLEE':
                self.acceleration += self.state_flee(time,
                                                     player, current_time, mobs)
            elif self.state == 'SACRIFICE':
                self.acceleration += self.state_sacrifice(
                    time, player, current_time)
            if self.init_state:
                if self.state == 'HURTING':
                    self.init_state = False
                    self.set_action(Animation_type.Hurt)
                elif self.state == 'IDLING':
                    self.set_action(Animation_type.Idle_Blinking)
                elif self.state == 'ATTACKING':
                    self.init_state = False
                    self.set_action(Animation_type.Kicking)

            self.rect.center += self.acceleration

            if self.rect.x + self.hitbox_x_offset < LEFT_BORDER:
                self.rect.x = LEFT_BORDER - self.hitbox_x_offset
            if(self.rect.x + self.rect.width + self.hitbox_x_offset > RIGHT_BORDER):
                self.rect.x = RIGHT_BORDER - self.rect.width - self.hitbox_x_offset
            self.hitbox.x = self.rect.x + self.hitbox_x_offset

            if self.rect.y + self.image_height - self.hitbox_y_offset < TOP_BORDER:
                self.rect.y = TOP_BORDER - self.image_height + self.hitbox_y_offset
            if self.rect.y + self.image_height - self.hitbox_y_offset > BOTTOM_BORDER:
                self.rect.y = BOTTOM_BORDER - self.image_height + self.hitbox_y_offset
            self.hitbox.y = self.rect.y + self.hitbox_y_offset

            print(
                f'{self.image.get_height(), self.image.get_width(), self.rect}')

            # print(
            #     f'{self.rect.y} & {self.rect.height} & {BOTTOM_BORDER, TOP_BORDER, LEFT_BORDER, TOP_BORDER}')

        elif self.state == self.states['DYING'] and not self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Dying)

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.rect.width, self.rect.height], 2)

        pygame.draw.rect(display, (255, 122, 0), [
                         self.rect.x - offset_x, self.rect.y - offset_y, self.rect.width, self.rect.height], 2)

        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox[0] -
                          offset_x, self.hitbox[1] - 15 - offset_y, self.hp_bar_width, 10))
        pygame.draw.rect(display, (0, 200, 0),
                         (self.hitbox[0] -
                          offset_x, self.hitbox[1] - 15 - offset_y, self.hp_bar_width - ((self.hp_bar_width/100)*(self.max_hp - self.health_points)), 10))

        pygame.draw.line(display, RED, self.hitbox.center - Vector2(offset_x,
                                                                    offset_y), (self.hitbox.center + self.vector3 * 25) - Vector2(offset_x,
                                                                                                                                  offset_y), 5)

        pygame.draw.line(display, GREEN, self.hitbox.center - Vector2(offset_x,
                                                                      offset_y), (self.hitbox.center + self.vector1 * 25) - Vector2(offset_x,
                                                                                                                                    offset_y), 5)

        pygame.draw.line(display, WHITE, self.hitbox.center - Vector2(offset_x,
                                                                      offset_y), (self.hitbox.center + self.vector2 * 25) - Vector2(offset_x,
                                                                                                                                    offset_y), 5)

    def hit(self, damage):
        if self.health_points - damage <= 0:
            self.is_alive = False
            self.state = self.states['DYING']
            self.health_points = 0
        elif self.is_alive and self.state != self.states['DYING'] and self.state != self.states['HURTING']:
            self.last_state = self.state
            self.state = self.states['HURTING']
            self.health_points -= damage
            self.init_state = True

    def state_seeking(self, time, player, current_time, mobs):
        if self.init_state:
            self.heading = pygame.Rect(
                randint(-268, 746), randint(-380, 1500), 1, 1)
            self.speed = 70
            self.timer = pygame.time.get_ticks()
            self.set_action(Animation_type.Walking)
            self.init_state = False

        if is_close(self.hitbox, player.rect, 200) or not self.health_points == self.max_hp:
            self.init_state = True
            self.state = self.states['HUNTING']

        if current_time - self.timer > 5000:
            self.set_destination()
            self.timer = pygame.time.get_ticks()

        return self.seek_with_approach(self.heading.center, time, mobs)

    def state_hunting(self, time, player, current_time, mobs):
        if self.init_state:
            self.speed = 150
            self.timer = pygame.time.get_ticks()
            self.set_action(Animation_type.Running)
            self.init_state = False

        if is_close(self.hitbox, player.rect, 25) and current_time - self.timer > 2000 and self.init_state:
            self.set_action(Animation_type.Kicking)
            self.init_state = False
            player.hit(self.damage)
            self.timer = pygame.time.get_ticks()

        return self.seek_with_approach(player.rect.center, time, mobs)

    def state_flee(self, time, player, current_time, mobs):
        if self.init_state:
            self.speed = 100
            self.timer = pygame.time.get_ticks()
            self.set_action(Animation_type.Running)
            self.init_state = False

        return self.flee(player.rect, time, mobs)

    def state_sacrifice(self):
        if self.init_state:
            self.speed = 200
            self.timer = pygame.time.get_ticks()
        pass

    def set_destination(self):
        self.heading = pygame.Rect(
            randint(-268 + 70, 746 - 70), randint(120 + 100, 640 - 100), 1, 1)

    def seek_with_approach(self, target, time, mobs):
        # vector from position -> target position
        self.desired = (
            target - Vector2(self.hitbox.centerx, self.hitbox.centery))
        self.vector1 = self.desired
        dist = self.desired.length()
        if not dist == 0:
            self.desired.normalize_ip()
            if dist < self.approach_radius:
                self.desired *= dist / self.approach_radius * self.speed * time
            else:
                self.desired *= self.speed * time

            # vector from acceleration vector to desired vector position
            steer = (self.desired - self.acceleration)

            # scale of vector to have correct length
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            self.avoid_mobs(mobs, time)
            return steer
        else:
            self.set_action(Animation_type.Idle_Blinking)
            return Vector2(0, 0)

    def flee(self, target, time, mobs):
        steer = Vector2(0, 0)
        distance = Vector2(self.hitbox.centerx - target.centerx,
                           self.hitbox.y - target.centery)
        self.desired = distance.normalize() * self.speed * time
        steer = (self.desired - self.acceleration)
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        self.avoid_mobs(mobs, time)
        return steer

    def avoid_mobs(self, mobs, time):
        for mob in mobs:
            if mob != self:
                distance = Vector2(self.hitbox.centerx - mob.hitbox.centerx,
                                   self.hitbox.centery - mob.hitbox.centery)
                self.vector3 = distance
                if 0 < distance.length() < 50:
                    self.acceleration += distance.normalize()
                    self.acceleration.scale_to_length(
                        self.desired.length())
                    self.vector2 = self.acceleration

    def update_animation(self):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Kicking) or self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 30

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.init_state = True
            elif self.action == int(Animation_type.Kicking):
                self.state = self.states['HUNTING']
                self.init_state = True
            elif self.action == int(Animation_type.Hurt):
                self.init_state = True
                if self.is_alive and self.health_points <= 20:
                    self.state = self.states['FLEE']
                elif self.is_alive:
                    self.state = self.last_state

            else:
                self.frame_index = 0

    def set_action(self, new_action):
        # check if the new action != previous
        if int(new_action) != self.action:
            self.action = new_action
            # update animation from start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
