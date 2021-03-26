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

        # id
        self.entity_id = 2

        self.is_alive = True

        # flip image based on direction
        self.flip = False
        # animations
        self.animation_list = entities_animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3

        # time for animation update
        self.update_time = 0

        # image properties
        self.image = self.animation_list[self.action][self.frame_index]
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

        # rect
        self.rect = self.image.get_rect(width=55, height=70)
        self.rect.x, self.rect.y = (x, y)

        # hitbox
        self.hitbox_x_offset = 30
        self.hitbox_y_offset = 15

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))
        # hp
        self.max_hp = 100
        self.health_points = 100
        self.hp_bar_width = self.rect.w

        # speed
        self.speed = 200
        self.acceleration = Vector2(0, 0)

        # cooldown on abilities
        self.cooldowns = {'attack': 2000, 'new_destination': 5000}
        self.attack_time = self.new_destination_time = -100000
        # attack damage
        self.damage = 5

        # how fast the acceleration vector follows desired vec
        self.max_force = 0.08
        self.approach_radius = 90

        # states
        self.states = {'SEEKING': 'SEEKING', 'HUNTING': 'HUNTING',
                       'FLEE': 'FLEE', 'SACRIFICE': 'SACRIFICE',
                       'HURTING': 'HURTING', 'DYING': 'DYING',
                       'ATTACKING': 'ATTACKING', 'IDLING': 'IDLING', 'APPEARING': 'APPEARING'}

        self.state = self.states['APPEARING']

        self.last_state = ''
        self.init_state = True

        # vector for desired location
        self.desired = Vector2(0, 0)

        # vectors that track position of player corners
        self.top_left = Vector2(0, 0)
        self.top_right = Vector2(0, 0)
        self.bottom_left = Vector2(0, 0)
        self.bottom_right = Vector2(0, 0)
        self.vector2 = Vector2(0, 0)
        self.vector = Vector2(0, 0)

    def update(self, time_passed, tick, player, mobs, stage):
        self.local_time = time_passed
        self.update_animation()
        if self.is_alive:
            if self.desired.x <= 0:
                self.flip = True
            else:
                self.flip = False

            if self.state == 'APPEARING':
                self.go_to = Vector2(
                    self.desired.x - self.rect.centerx, self.desired.y - self.rect.centery)
                self.set_action(Animation_type.Running)
                if self.go_to.x <= 0:
                    self.flip = True
                else:
                    self.flip = False
                if abs(self.go_to.x) > 5:
                    self.go_to.normalize_ip()
                    self.rect.centerx += self.go_to.x * self.speed * tick
                    self.hitbox.x = self.rect.x + self.hitbox_x_offset
                    self.hitbox.y = self.rect.y + self.hitbox_y_offset
                else:
                    self.state = self.states['SEEKING']
                    self.set_action(Animation_type.Walking)
            else:
                if self.state == 'SEEKING':
                    self.acceleration += self.state_seeking(
                        tick, player, mobs)
                elif self.state == 'HUNTING':
                    self.acceleration += self.state_hunting(
                        tick, player, mobs)
                elif self.state == 'FLEE':
                    self.acceleration += self.state_flee(tick,
                                                         player, mobs)
                elif self.state == 'SACRIFICE':
                    self.acceleration += self.state_sacrifice(
                        tick, player)
                if self.init_state:
                    if self.state == 'HURTING':
                        self.init_state = False
                        self.set_action(Animation_type.Hurt)
                    elif self.state == 'IDLING':
                        self.set_action(Animation_type.Idle_Blinking)
                    elif self.state == 'ATTACKING':
                        self.init_state = False
                        self.set_action(Animation_type.Kicking)

                self.avoid_mobs(mobs)
                self.rect.center += self.acceleration

                check_boundaries_for_x(self)
                self.hitbox.x = self.rect.x + self.hitbox_x_offset

                check_boundaries_for_y(self)
                self.hitbox.y = self.rect.y + self.hitbox_y_offset

        elif self.state == self.states['DYING'] and not self.init_state:
            self.set_action(Animation_type.Dying)

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.rect.width, self.rect.height], 2)

        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox.x -
                          offset_x, self.hitbox.y - 15 - offset_y, self.hp_bar_width, 10))
        if self.is_alive:
            pygame.draw.rect(display, (0, 200, 0),
                             (self.hitbox.x -
                              offset_x, self.hitbox.y - 15 - offset_y, self.hp_bar_width - ((self.hp_bar_width/100)*(self.max_hp - self.health_points)), 10))

        # pygame.draw.line(display, RED, self.hitbox.center - Vector2(offset_x,
        #                                                             offset_y), (self.hitbox.center + self.vector3 * 25) - Vector2(offset_x,
        #                                                                                                                           offset_y), 5)

        # pygame.draw.line(display, GREEN, self.hitbox.center - Vector2(offset_x,
        #                                                               offset_y), (self.hitbox.center + self.vector1 * 25) - Vector2(offset_x,
        #                                                                                                                             offset_y), 5)

        pygame.draw.line(display, WHITE, self.hitbox.center - Vector2(offset_x,
                                                                      offset_y), (self.hitbox.center + self.vector2 * 25) - Vector2(offset_x,
                                                                                                                                    offset_y), 5)

    def hit(self, damage):
        if self.health_points - damage <= 0:
            self.is_alive = False
            self.state = self.states['DYING']
            self.health_points = 0
            mob_death_sound.play()
        elif self.is_alive and self.state == self.states['HURTING']:
            self.frame_index = 0
            self.init_state = False
            self.health_points -= damage

        elif self.is_alive and self.state != self.states['DYING']:
            self.last_state = self.state
            self.state = self.states['HURTING']
            self.health_points -= damage
            self.init_state = True

    def state_seeking(self, time, player, mobs):
        if self.init_state:
            self.heading = pygame.Rect(
                randint(-268, 746), randint(-380, 1500), 1, 1)
            self.speed = 70
            self.set_action(Animation_type.Walking)
            self.init_state = False

        if is_close(self.hitbox, player.hitbox, 200) or not self.health_points == self.max_hp:
            self.init_state = True
            self.state = self.states['HUNTING']

        if self.local_time - self.new_destination_time > self.cooldowns['new_destination']:
            self.new_destination_time = self.local_time
            self.set_destination()

        return self.seek_with_approach(self.heading.center, time, mobs)

    def state_hunting(self, time, player, mobs):
        if self.init_state:
            self.speed = 150
            self.set_action(Animation_type.Running)
            self.init_state = False

        if is_close(self.hitbox, player.hitbox, 30) and self.local_time - self.attack_time > self.cooldowns['attack']:
            self.attack_time = self.local_time
            self.set_action(Animation_type.Kicking)
            self.init_state = False
            player.hit(self.damage)

        # self.top_left = Vector2(
        #     player.hitbox.topleft[0] - self.hitbox.center[0], player.hitbox.topleft[1] - self.hitbox.center[1]).length()
        # self.top_right = Vector2(player.hitbox.topright[0] - self.hitbox.center[0],
        #                          player.hitbox.topright[1] - self.hitbox.center[1]).length()
        # self.bottom_left = Vector2(
        #     player.hitbox.bottomleft[0] - self.hitbox.center[0], player.hitbox.bottomleft[1] - self.hitbox.center[1]).length()
        # self.bottom_right = Vector2(
        #     player.hitbox.bottomright[0] - self.hitbox.center[0], player.hitbox.bottomright[1] - self.hitbox.center[1]).length()

        # print(
        #     f'{self.top_left,self.top_right,self.bottom_left,self.bottom_right}')

        return self.seek_with_approach(player.hitbox.center, time, mobs)

    def state_flee(self, tick, player, mobs):
        if self.init_state:
            self.speed = 100
            self.set_action(Animation_type.Running)
            self.init_state = False

        return self.flee(player.hitbox, tick, mobs)

    def set_destination(self):
        self.heading = pygame.Rect(
            randint(-268 + 70, 746 - 70), randint(120 + 100, 640 - 100), 1, 1)

    def seek_with_approach(self, target, tick, mobs):
        # vector from position -> target position
        self.desired = (
            target - Vector2(self.hitbox.centerx, self.hitbox.centery))
        distance_length = self.desired.length()
        if not distance_length == 0:
            self.desired.normalize_ip()
            if distance_length < self.approach_radius:
                self.desired *= distance_length / self.approach_radius * self.speed * tick
            else:
                self.desired *= self.speed * tick

            # vector from acceleration vector to desired vector position
            steer = (self.desired - self.acceleration)

            # scale of vector to have correct length
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            return steer
        else:
            self.set_action(Animation_type.Idle_Blinking)
            return Vector2(0, 0)

    def flee(self, target, tick, mobs):
        steer = Vector2(0, 0)
        distance = Vector2(self.hitbox.centerx - target.centerx,
                           self.hitbox.y - target.centery)
        distance_length = self.desired.length()
        if not distance_length == 0:
            self.desired = distance.normalize() * self.speed * tick
            steer = (self.desired - self.acceleration)
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
        else:
            return Vector2(0, 0)
        return steer

    def avoid_mobs(self, mobs):
        for mob in mobs:
            if mob != self:
                distance = Vector2(self.hitbox.centerx - mob.hitbox.centerx,
                                   self.hitbox.centery - mob.hitbox.centery)
                if 0 < distance.length() < 50:
                    self.acceleration += distance.normalize()
                    self.acceleration.scale_to_length(
                        self.desired.length())
                    self.vector2 = self.acceleration
                elif distance.length() == 0:
                    self.acceleration += Vector2(0, 0)

    def update_animation(self):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame

        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Kicking) or self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 30

        if self.local_time - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = self.local_time
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
            self.update_time = self.local_time
