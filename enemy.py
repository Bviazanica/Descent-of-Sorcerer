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
        # image
        self.images = []
        self.enemy_img = pygame.image.load(
            'data/images/entities/enemy/Idle/0.png').convert_alpha()
        enemy_img = pygame.transform.scale(self.enemy_img, (72, 128))
        self.images.append(enemy_img)
        self.image = self.images[0]
        self.rect = self.image.get_rect(width=(70), height=(100))

        self.rect.center = (x, y)

        # hitbox
        self.hitbox = pygame.Rect(self.rect.x + 10, self.rect.y + 35, 70, 100)
        # hp
        self.max_hp = 100
        self.health_points = 100

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
                       'FLEE': 'FLEE', 'SACRIFICE': 'SACRIFICE'}
        self.state = self.states['SEEKING']

        self.init_state = True

        self.timer = 0

        self.top_border, self.bottom_border = -268, 746
        self.left_border, self.right_border = -380, 1500
        self.player_border_min_y, self.player_border_max_y = 120, 640

        self.vector1 = Vector2(0, 0)
        self.vector2 = Vector2(0, 0)
        self.vector3 = Vector2(0, 0)
        self.vector4 = Vector2(0, 0)

    def update(self, time, player, current_time, mobs):
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

        # print(self.acceleration.length())

        if(self.rect.x < self.left_border):
            self.rect.x = self.left_border
        if(self.rect.x > self.right_border - self.rect.width):
            self.rect.x = self.right_border - self.rect.width

        if(self.rect.y < self.player_border_min_y):
            self.rect.y = self.player_border_min_y
        if(self.rect.y > self.player_border_max_y - self.rect.height):
            self.rect.y = self.player_border_max_y - self.rect.height

        self.rect.center += self.acceleration

        self.hitbox[0] = self.rect.x + 10
        self.hitbox[1] = self.rect.y + 35

    def draw(self, display, offset_x, offset_y, player):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))
        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox[0] - offset_x, self.hitbox[1] - offset_y, 70, 100], 2)

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
        self.health_points -= damage

    def state_seeking(self, time, player, current_time, mobs):
        if self.init_state:
            self.heading = pygame.Rect(
                randint(-268, 746), randint(-380, 1500), 70, 100)
            self.speed = 100
            self.timer = pygame.time.get_ticks()
            self.init_state = False

        if is_close(self.hitbox, player.rect, 200) or not self.health_points == self.max_hp:
            self.state = self.states['HUNTING']
            self.init_state = True
        elif self.health_points <= 20:
            self.state = self.states['FLEE']
            self.init_state = True

        if current_time - self.timer > 5000:
            self.set_destination()
            self.timer = pygame.time.get_ticks()

        return self.seek_with_approach(self.heading.center, time, mobs)

    def state_hunting(self, time, player, current_time, mobs):
        if self.init_state:
            self.speed = 150
            self.timer = pygame.time.get_ticks()
            self.init_state = False

        # elif self.health_points <= 20:
        #     self.state = self.states['FLEE']
        #     self.init_state = True

        if is_close(self.hitbox, player.rect, 25) and current_time - self.timer > 2000:
            player.hit(self.damage)
            self.timer = pygame.time.get_ticks()

        return self.seek_with_approach(player.rect.center, time, mobs)

    def state_flee(self, time, player, current_time):
        if self.init_state:
            self.speed = 100
            self.timer = pygame.time.get_ticks()
            self.init_state = False

        # if not is_close(self.hitbox, player.rect, 200):
        #     # if boss exist -> sacrifice
        #     # else seek with regeneration
        #     self.state = self.states['SEEKING']
        #     self.init_state = True

        return self.flee(player.rect, time)

    def state_sacrifice(self):
        if self.init_state:
            self.speed = 200
            self.timer = pygame.time.get_ticks()
            self.init_state = False
        pass

    def set_destination(self):
        self.heading = pygame.Rect(
            randint(-268 + 70, 746 - 70), randint(120 + 100, 640 - 100), 70, 100)

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
            return Vector2(0, 0)

    def flee(self, target, time):
        steer = Vector2(0, 0)
        distance = Vector2(self.hitbox.centerx - target.centerx,
                           self.hitbox.y - target.centery)
        self.desired = distance.normalize() * self.speed * time
        steer = (self.desired - self.acceleration)
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)

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
