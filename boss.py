import random
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
Vector2 = pygame.math.Vector2


class Boss():
    def __init__(self):
        self.type = 'boss'

        # id
        self.entity_id = 1

        self.is_alive = True

        # animations
        self.animation_list = animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3

        # id for animations
        self.entity_id = 1
        # time since class is iniciated
        self.update_time = pygame.time.get_ticks()

        # flip image based on direction
        self.flip = False

        # image properties
        self.image = self.animation_list[self.action][self.frame_index]
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # rect
        self.rect = self.image.get_rect(width=90, height=125)
        self.rect.center = 200, 200

        # hitbox
        self.hitbox_x_offset = 50
        self.hitbox_y_offset = 45

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        # cooldown on abilities
        self.cooldowns = {'summon': 15000, 'whirlwind': 10000, 'orbs': 5000}

        # speed
        self.speed = 200
        # health points & bars properties
        self.max_hp = 300
        self.health_points = 300

        self.hp_bar_width = self.rect.w

        self.projectiles = []

        # desired location vector
        self.desired = Vector2(0, 0)

        # states
        self.states = {'HURTING': 'HURTING', 'DYING': 'DYING', 'SUMMONING': 'SUMMONING',
                       'ATTACKING': 'ATTACKING', 'IDLING': 'IDLING', 'FIRING': 'FIRING', 'APPEARING': 'APPEARING'}

        self.state = self.states['IDLING']
        self.init_state = True
        self.last_state = ''

        self.ready_to_attack = False

    def update(self, display, player, time, movement, entities):
        new_entities = new_list_without_self(self, entities)
        self.desired = (
            player.hitbox.center - Vector2(self.hitbox.centerx, self.hitbox.centery))
        self.update_animation()

        if self.is_alive:
            if self.desired[0] <= 0:
                self.flip = True
            else:
                self.flip = False
        if self.init_state:
            if self.state == 'IDLING':
                self.set_action(Animation_type.Idle_Blinking)
            elif self.state == 'HURTING':
                self.init_state = False
                self.set_action(Animation_type.Hurt)
            elif self.state == 'DYING':
                self.init_state = False
                self.set_action(Animation_type.Dying)
            elif self.state == 'SUMMONING':
                self.init_state = False
                self.set_action(Animation_type.Summoning)
            elif self.state == 'ATTACKING':
                self.init_state = False
                self.set_action(Animation_type.Slashing_in_The_Air)
            elif self.state == 'FIRING':
                self.init_state = False
                self.set_action(Animation_type.Throwing_in_The_Air)
                self.fire(player.hitbox.center, time)
            elif self.state == 'APPEARING':
                self.init_state = False
                self.set_action(Animation_type.Walking)
                self.appear()

        if(self.projectiles):
            for projectile in self.projectiles:
                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list):
                    for col in collision_list:
                        col.hit(projectile.damage)
                    self.projectiles.pop(self.projectiles.index(projectile))

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER or projectile.rect.y < TOP_BORDER or projectile.rect.y > BOTTOM_BORDER:
                    self.projectiles.pop(self.projectiles.index(projectile))

                else:
                    projectile.update(time)

        check_boundaries_for_x(self)
        self.hitbox.x = self.rect.x + self.hitbox_x_offset
        check_boundaries_for_y(self)
        self.hitbox.y = self.rect.y + self.hitbox_y_offset

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox[0] - offset_x, self.hitbox[1] - offset_y, self.rect.width, self.rect.height], 2)

        # healthbar
        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox[0] - offset_x, self.hitbox[1] - 15 - offset_y, 75, 10))
        pygame.draw.rect(display, (0, 200, 0),
                         (self.hitbox[0] - offset_x, self.hitbox[1] - 15 - offset_y, self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)), 10))

        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)

    def fire(self, target, time):
        self.desired = target - \
            Vector2(self.hitbox.centerx, self.hitbox.centery)
        self.desired.normalize_ip()
        projectile = Projectile(self.hitbox.center, 1, self.desired, 'boss')
        self.projectiles.append(projectile)

    def whirlwind(self, player):
        if is_close(self.hitbox, player.hitbox, 200):
            self.damage = 20
            player.hit(self.damage)
            # maybe throwback the player in opposite vector

    def heal(self, heal_amount):
        self.health_points += heal_amount

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

    def appear(self):
        if self.rect.x > 800:
            self.rect.x -= 2

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
            elif self.action == int(Animation_type.Hurt):
                self.init_state = True
                if self.is_alive:
                    self.state = self.last_state
            elif self.action == int(Animation_type.Slashing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
            elif self.action == int(Animation_type.Throwing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
            elif self.action == int(Animation_type.Summoning):
                self.state = self.states['IDLING']
                self.init_state = True
            else:
                self.frame_index = 0

    def set_action(self, new_action):
        # check if the new action != previous
        if int(new_action) != self.action:
            self.action = new_action
            # update animation from start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
