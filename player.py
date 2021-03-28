import os
import sys
import pygame
import random
from utility import *
from pygame.locals import *
from projectile import Projectile
from data.globals.globals import *
from data.gameobjects.vector2 import Vector2


class Player():
    def __init__(self, x, y):
        self.type = 'player'

        # id
        self.entity_id = 0

        self.is_alive = True
        # animations
        self.action = 3
        self.frame_index = 0
        self.animation_list = entities_animation_list[self.entity_id]

        # local update time for animations
        self.update_time = 0

        self.animation_time = 0
        # image properties
        self.flip = False
        self.image = self.animation_list[self.action][self.frame_index]
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()

        self.fireball_icon = pygame.image.load(
            'data/images/icons/new/fireball_icon.png').convert_alpha()
        self.staff_icon = pygame.image.load(
            'data/images/icons/new/staff.png').convert()

        self.rect = self.image.get_rect(width=70, height=80)
        self.rect.center = x, y
        # hitbox
        self.hitbox_x_offset = 25
        self.hitbox_y_offset = 20

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        self.collision_hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset*2, self.rect.y + self.hitbox_y_offset*2, self.rect.width/3, self.rect.height/2))

        self.facing_positive = True
        # cooldowns
        self.cooldowns = {'melee': 2000, 'range': 2000}
        # player cooldownsdd
        self.melee_attack_time = self.range_attack_time = -100000
        # attack damage
        self.melee_damage = 2000

        # speed
        self.speed = 250

        # projectiles
        self.projectiles = []
        self.projectile_damage = 4000
        self.projectile_speed = 400

        # healthpoints
        self.health_points = 2000
        self.max_hp = 2000
        self.hp_bar_width = 400
        self.states = {'IDLING': 'IDLING', 'RUNNING': 'RUNNING',
                       'ATTACKING': 'ATTACKING', 'FIRING': 'FIRING', 'DYING': 'DYING',
                       'HURTING': 'HURTING', 'RUNNING-FIRING': 'RUNNING-FIRING',
                       'RUNNING-ATTACKING': 'RUNNING-ATTACKING'}
        self.state = self.states['IDLING']

        self.init_state = True
        self.death_screen_ready = False
        self.ready_to_fire = True

    # update position

    def update(self, time_passed, time, movement, entities, stage):
        self.update_time = time_passed
        new_entities = new_list_without_self(self, entities)
        self.update_animation()
        if self.projectiles:
            for projectile in self.projectiles:
                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list):
                    for col in collision_list:
                        if not col.state == col.states['APPEARING']:
                            col.hit(projectile.damage)
                            fireball_hit_sound.play()
                    projectile.update(self.update_time, time,
                                      self.projectiles, True)

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER:
                    self.projectiles.pop(
                        self.projectiles.index(projectile))

                else:
                    projectile.update(self.update_time, time, [], False)

        if self.init_state or self.state == self.states['HURTING']:
            if self.facing_positive:
                self.flip = False
            else:
                self.flip = True
        if self.init_state and self.is_alive:
            if self.state == 'IDLING':
                self.set_action(Animation_type.Idle_Blinking)
            elif self.state == 'RUNNING':
                self.set_action(Animation_type.Running)
            elif self.state == 'HURTING':
                self.init_state = False
                self.set_action(Animation_type.Hurt)
            elif self.state == 'RUNNING-ATTACKING':
                self.state_running_attacking(new_entities)
            elif self.state == 'RUNNING-FIRING':
                self.state_running_firing()
            elif self.state == 'ATTACKING':
                self.init_state = False
                self.set_action(Animation_type.Slashing)
                self.melee_attack(new_entities)
            elif self.state == 'FIRING':
                self.init_state = False
                self.set_action(Animation_type.Throwing_in_The_Air)
        self.rect, collisions = self.move(
            self.rect, movement, new_entities, time)

        self.collision_hitbox.x = self.rect.x + self.hitbox_x_offset*2
        self.collision_hitbox.y = self.rect.y + self.hitbox_y_offset*2
        # print(
        #     f'STATE {self.state}, ACTION {self.action}, HP {self.health_points}')

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

        check_boundaries_for_x(self)
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
        check_boundaries_for_y(self)
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
        pygame.draw.rect(display, RED, [self.collision_hitbox.x - offset_x, self.collision_hitbox.y -
                                        offset_y, self.collision_hitbox.width, self.collision_hitbox.height], 2)

        pygame.draw.rect(display, BLACK,
                         (4, 4, self.hp_bar_width+2, 22))

        pygame.draw.rect(display, RED,
                         (5, 5, self.hp_bar_width, 20))
        if self.is_alive:
            pygame.draw.rect(display, GREEN,
                             (5, 5, self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)), 20))

        if get_cooldown_ready(self.range_attack_time, self.cooldowns['range'],  self.update_time):
            pygame.draw.circle(display, GREEN, (25, 50), 20)
        else:
            pygame.draw.circle(display, RED, (25, 50), 20)

        if get_cooldown_ready(self.melee_attack_time, self.cooldowns['melee'], self.update_time):
            pygame.draw.circle(display, GREEN, (70, 50), 20)
        else:
            pygame.draw.circle(display, RED, (70, 50), 20)
        display.blit(self.fireball_icon, (5, 40))
        display.blit(self.staff_icon, (65, 40))

    def hit(self, damage):
        if self.health_points - damage <= 0:
            self.is_alive = False
            self.state = self.states['DYING']
            self.health_points = 0
            self.set_action(Animation_type.Dying)
        elif self.is_alive and self.state == self.states['HURTING']:
            self.frame_index = 0
            self.init_state = False
            self.health_points -= damage
            hit_sound.play()
        elif self.is_alive and self.state != self.states['DYING']:
            self.frame_index = 0
            self.set_action(Animation_type.Hurt)
            if self.state != self.states['FIRING'] or self.state != self.states['ATTACKING'] or self.state != self.states['RUNNING-FIRING'] or self.state != self.states['RUNNING-ATTACKING']:
                self.state = self.states['HURTING']
                self.init_state = False
            self.health_points -= damage
            hit_sound.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Slashing) or self.action == int(Animation_type.Throwing_in_The_Air):
            ANIMATION_COOLDOWN = 30
        if self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 15

        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1

        if (self.action == int(Animation_type.Throwing_in_The_Air) or self.action == int(Animation_type.Throwing_in_The_Air)) and self.frame_index == 2 and self.ready_to_fire:
            self.fire()
            self.ready_to_fire = False
        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.death_screen_ready = True
            elif self.action == int(Animation_type.Slashing):
                self.init_state = True
                self.state = self.states['IDLING']
            elif self.action == int(Animation_type.Throwing_in_The_Air):
                self.ready_to_fire = True
                self.init_state = True
                self.state = self.states['IDLING']
            elif self.action == int(Animation_type.Run_Slashing):
                self.init_state = True
                self.state = self.states['RUNNING']
            elif self.action == int(Animation_type.Run_Throwing):
                self.ready_to_fire = True
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
            self.animation_time = self.update_time

    def melee_attack(self, new_entities):
        swing_sound.play()
        self.melee_attack_time = self.update_time
        if self.facing_positive:
            attack = pygame.Rect(self.rect.x + ((self.rect.w - self.hitbox_x_offset)), self.rect.y,
                                 self.rect.width, self.rect.height)
        else:
            attack = pygame.Rect(
                ((self.rect.x + self.hitbox_x_offset - self.rect.w)), self.rect.y, self.rect.width, self.rect.height)

        collision_list = check_collision(attack, new_entities)
        for col in collision_list:
            if not col.state == col.states['APPEARING']:
                col.hit(self.melee_damage)
                bonk_sound.play()

    def fire(self):
        random.choice([fireball_cast_sound, fireball_cast2_sound]).play()
        self.range_attack_time = self.update_time
        if self.facing_positive:
            direction = 1
            projectile = Projectile(
                Vector2(self.hitbox.x + self.hitbox.w, self.hitbox.centery), direction, Vector2(0, 0), 1, self.projectile_damage, self.projectile_speed)
        else:
            direction = -1
            projectile = Projectile(
                Vector2(self.hitbox.x, self.hitbox.centery), direction, Vector2(0, 0), 1, self.projectile_damage, self.projectile_speed)

        self.projectiles.append(projectile)

    def state_running_attacking(self, new_entities):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Slashing)
            self.melee_attack(new_entities)

    def state_running_firing(self):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Throwing)
            self.fire()
