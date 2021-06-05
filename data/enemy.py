import math
import pygame
from data.utility import *
from random import randint
from pygame.locals import *
from data.globals.globals import *
Vector2 = pygame.math.Vector2


class Enemy():
    def __init__(self, x, y, spawned, entities_animation_list):
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

        # flee timer
        self.flee_time = 0
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

        self.min_distance = 0
        # speed
        self.speed = 200
        self.acceleration = Vector2(0, 0)

        # cooldown on abilities
        self.cooldowns = {'attack': 2000, 'new_destination': 5000}
        self.attack_time = self.new_destination_time = -100000
        # attack damage
        self.damage = 10

        # how fast the acceleration vector follows desired vec
        self.max_force = 0.08
        self.approach_radius = 90

        # states
        self.states = {'SEEKING': 'SEEKING', 'HUNTING': 'HUNTING',
                       'FLEE': 'FLEE', 'SACRIFICE': 'SACRIFICE',
                       'HURTING': 'HURTING', 'DYING': 'DYING',
                       'ATTACKING': 'ATTACKING', 'IDLING': 'IDLING', 'APPEARING': 'APPEARING'}

        # spawned mobs by boss dont have appearing state
        if spawned:
            self.state = self.states['APPEARING']
        else:
            self.state = self.states['SEEKING']

        self.last_state = ''
        self.init_state = True

        # vector for desired location
        self.desired = Vector2(0, 0)

        self.go_to = Vector2(0, 0)

    def update(self, time_passed, tick, player, mobs, stage, boss, entities):
        self.local_time = time_passed
        self.update_animation()
        # targets that mob will hunt
        new_targets = list(filter(lambda x: x.type ==
                                  'player' or x.type == 'decoy', entities))

        # state management
        if self.is_alive:
            if self.state == 'APPEARING':
                self.speed = 120
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
            else:
                if self.state == 'SEEKING':
                    self.acceleration += self.state_seeking(
                        tick, new_targets)
                elif self.state == 'HUNTING':
                    self.acceleration += self.state_hunting(
                        tick, player, new_targets)
                elif self.state == 'FLEE':
                    self.acceleration += self.state_flee(tick,
                                                         player, boss)
                elif self.state == 'SACRIFICE':
                    self.acceleration += self.state_sacrifice(
                        tick, boss)
                if self.init_state:
                    if self.state == 'HURTING':
                        self.init_state = False
                        self.set_action(Animation_type.Hurt)
                    elif self.state == 'IDLING':
                        self.set_action(Animation_type.Idle_Blinking)
                    elif self.state == 'ATTACKING':
                        self.init_state = False
                        self.set_action(Animation_type.Kicking)

                # avoiding other mobs
                self.avoid_mobs(mobs)
                self.rect.center += self.acceleration

                # boundaries of map
                check_boundaries_for_x(self)
                self.hitbox.x = self.rect.x + self.hitbox_x_offset
                check_boundaries_for_y(self)
                self.hitbox.y = self.rect.y + self.hitbox_y_offset
                if self.acceleration.x <= 0:
                    self.flip = True
                else:
                    self.flip = False

        # dying state
        elif self.state == self.states['DYING'] and not self.init_state:
            self.set_action(Animation_type.Dying)

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))
        pygame.draw.rect(display, RED,
                         (self.hitbox.x - offset_x, self.hitbox.y - 10 - offset_y, self.hp_bar_width, 10))
        if self.is_alive:
            pygame.draw.rect(display, GREEN,
                             (self.hitbox.x -
                              offset_x, self.hitbox.y - 10 - offset_y, int(self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points))), 10))

    # getting hit
    def hit(self, damage):
        if self.health_points - damage <= 0 and self.state != self.states['DYING']:
            self.is_alive = False
            self.state = self.states['DYING']
            self.health_points = 0
            self.init_state = False
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

    # seeking state function
    def state_seeking(self, time, new_entities):
        if self.init_state:
            self.heading = pygame.Rect(
                randint(-268, 746), randint(-380, 1500), 1, 1)
            self.speed = 70
            self.set_action(Animation_type.Walking)
            self.init_state = False

        # if any target is in area, chase it
        for target in new_entities:
            if is_close(self.hitbox, target.hitbox, 200) or not self.health_points == self.max_hp:
                self.init_state = True
                self.state = self.states['HUNTING']
                break

        # determine new location to walk
        if self.local_time - self.new_destination_time > self.cooldowns['new_destination']:
            self.new_destination_time = self.local_time
            self.set_destination()

        return self.seek_with_approach(self.heading.center, time)

    # hunting state
    def state_hunting(self, time, player, new_targets):
        if self.init_state:
            self.speed = 150
            self.set_action(Animation_type.Running)
            self.init_state = False

        # distance between mob and player
        new_distance = Vector2(
            player.hitbox.centerx - self.hitbox.centerx, player.hitbox.centery - self.hitbox.centery)
        self.min_distance = new_distance.length()
        # target nearest entity, prefer decoy over player
        new_target = player
        new_targets = list(filter(lambda x: x.type == 'decoy', new_targets))
        if len(new_targets):
            for target in new_targets:
                if is_close(self.hitbox, target.hitbox, 200) and new_target == player:
                    new_distance = Vector2(
                        target.hitbox.centerx - self.hitbox.centerx, target.hitbox.centery - self.hitbox.centery)
                    if new_distance.length() < self.min_distance:
                        self.min_distance = new_distance.length()
                        new_target = target

        # attack if near the target
        if is_close(self.hitbox, new_target.hitbox, 50):
            self.set_action(Animation_type.Walking)
            if self.local_time - self.attack_time > self.cooldowns['attack']:
                self.attack_time = self.local_time
                self.state = self.states['ATTACKING']
                self.set_action(Animation_type.Kicking)
                self.init_state = False
                new_target.hit(self.damage)
        else:
            self.set_action(Animation_type.Running)

        return self.seek_with_approach(new_target.hitbox.center, time)

    # flee state, if low hp
    def state_flee(self, tick, player, boss):
        if self.init_state:
            self.flee_time = self.local_time
            self.speed = 100
            self.set_action(Animation_type.Running)
            self.init_state = False

        # sacrifice if boss fight is on
        if boss:
            if self.local_time - self.flee_time > 5000 and boss.is_alive:
                self.state = self.states['SACRIFICE']
                self.set_action(Animation_type.Walking)

        return self.flee(player.hitbox, tick)

    # sacrifice state, when low hp, goes to feed the boss
    def state_sacrifice(self, tick, boss):
        if self.init_state:
            self.speed = 70
            self.set_action(Animation_type.Walking)
            self.init_state = False
            self.flee_time = self.local_time

        if self.hitbox.colliderect(boss.hitbox):
            self.is_alive = False
            self.init_state = True
            boss.heal(50)

        if not boss.is_alive:
            self.state = self.states['FLEE']

        return self.seek_with_approach(boss.hitbox.center, tick)

    # generate seek destination
    def set_destination(self):
        self.heading = pygame.Rect(
            randint(-268 + 70, 746 - 70), randint(120 + 100, 640 - 100), 1, 1)

    # tracking the target, plus steering
    def seek_with_approach(self, target, tick):
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

    # flee from
    def flee(self, target, tick):
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

    # avoiding other mobs
    def avoid_mobs(self, mobs):
        for mob in mobs:
            if mob != self:
                distance = Vector2(self.hitbox.centerx - mob.hitbox.centerx,
                                   self.hitbox.centery - mob.hitbox.centery)
                if 0 < distance.length() < 50 and self.acceleration.length() != 0:
                    self.acceleration += distance.normalize()
                    self.acceleration.scale_to_length(2.0)
                elif distance.length() == 0:
                    self.acceleration += Vector2(0, 0)

    # animations management
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
                if self.is_alive and self.health_points <= self.max_hp//5:
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
