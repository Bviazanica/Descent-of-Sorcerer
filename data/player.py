import os
import sys
import pygame
import random
from data.utility import *
from pygame.locals import *
from data.globals.globals import *
from data.lightning import Lightning
from data.projectile import Projectile
from data.gameobjects.vector2 import Vector2


class Player():
    def __init__(self, x, y):
        self.type = 'player'

        # id
        self.entity_id = 0

        self.is_alive = True

        self.boosted = False
        self.boosted_timer = 0

        self.invulnerability = False
        self.invulnerability_timer = 0
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

        # effects of potions
        self.effects = []

        self.fireball_icon = pygame.image.load(
            'data/images/icons/new/fireball_icon.png').convert_alpha()
        self.staff_icon = pygame.image.load(
            'data/images/icons/new/staff.png').convert()
        self.lightning_icon = pygame.image.load(
            'data/images/icons/new/lightning_icon.png').convert_alpha()

        self.invulnerability_icon = pygame.image.load(
            'data/images/icons/new/invulnerability.png').convert_alpha()
        self.power_icon = pygame.image.load(
            'data/images/icons/new/power.png').convert()

        self.effect_icon_width = self.power_icon.get_width()
        self.effect_icon_height = self.power_icon.get_height()

        self.rect = self.image.get_rect(width=70, height=80)
        self.rect.center = x, y
        # hitbox
        self.hitbox_x_offset = 25
        self.hitbox_y_offset = 20

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        self.facing_positive = True
        # cooldowns
        self.cooldowns = {'melee': 2000, 'range': 1000,
                          'lightning': 1000}
        # mana costs
        self.mana_costs = {'fireball': 15, 'lightning': 50}
        # player cooldownsdd
        self.melee_attack_time = self.fireball_time = self.lightning_time = -100000
        # attack damage
        self.melee_damage = 100

        # speed
        self.speed = 250

        # spells
        self.lightnings = []

        # projectiles
        self.projectiles = []
        self.projectile_damage = 5
        self.projectile_speed = 400

        # healthpoints
        self.health_points = 200
        self.max_hp = 200
        self.hp_bar_width = 300

        # mana
        self.mana_points = 200
        self.max_mp = 200
        self.mana_bar_width = 300

        self.mana_regeneration = 0.1

        self.states = {'IDLING': 'IDLING', 'RUNNING': 'RUNNING',
                       'ATTACKING': 'ATTACKING', 'FIRING': 'FIRING', 'DYING': 'DYING',
                       'HURTING': 'HURTING', 'RUNNING-FIRING': 'RUNNING-FIRING',
                       'RUNNING-ATTACKING': 'RUNNING-ATTACKING'}
        self.state = self.states['IDLING']

        self.init_state = True
        self.death_screen_ready = False
        self.ready_to_fire = True
        self.ready_to_attack = True

        self.casting = ''

    # update position

    def update(self, time_passed, time, movement, entities, stage):
        self.update_time = time_passed
        new_entities = new_list_without_self(self, entities)
        self.update_animation(new_entities)

        if self.init_state or self.state == self.states['HURTING']:
            if self.facing_positive:
                self.flip = False
            else:
                self.flip = True

        if self.is_alive:
            if self.init_state:
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
            self.rect = self.move(
                self.rect, movement, time)

            self.regenerate_mana(self.mana_regeneration)

            if self.boosted and self.update_time - self.boosted_timer > 5000:
                self.boosted = False
                if self.power_icon in self.effects:
                    self.effects.pop(self.effects.index(self.power_icon))
            if self.invulnerability and self.update_time - self.invulnerability_timer > 5000:
                self.invulnerability = False
                if self.invulnerability_icon in self.effects:
                    self.effects.pop(self.effects.index(
                        self.invulnerability_icon))

        if self.projectiles:
            for projectile in self.projectiles:
                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list) and not projectile.destroy:
                    projectile.destroy = True
                    for col in collision_list:
                        if not col.state == col.states['APPEARING']:
                            col.hit(projectile.damage)
                            fireball_hit_sound.play()
                    projectile.update(self.update_time, time,
                                      self.projectiles)

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER:
                    self.projectiles.pop(
                        self.projectiles.index(projectile))

                else:
                    projectile.update(self.update_time, time, self.projectiles)

        if self.lightnings:
            for lightning in self.lightnings:
                lightning.update(self.update_time,
                                 self.lightnings, new_entities)

    def move(self, rect, movement, time):

        self.rect.x += movement[0] * time * self.speed
        check_boundaries_for_x(self)
        self.hitbox.x = self.rect.x + self.hitbox_x_offset

        self.rect.y += movement[1] * time * self.speed
        check_boundaries_for_y(self)
        self.hitbox.y = self.rect.y + self.hitbox_y_offset

        return self.rect
    # draw player to canvas

    def draw(self, display, offset_x, offset_y, player):
        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)
        if self.lightnings:
            for lg in self.lightnings:
                lg.draw(display, offset_x, offset_y)
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))
        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.rect.width, self.rect.height], 2)

        pygame.draw.rect(display, BLACK,
                         (4, 4, self.hp_bar_width+2, 22), 1)

        pygame.draw.rect(display, RED,
                         (5, 5, self.hp_bar_width, 20))
        healthbar_width = int(
            self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)))
        if self.is_alive:
            pygame.draw.rect(display, GREEN,
                             (5, 5, healthbar_width, 20))

        mana_bar_width = int(
            self.mana_bar_width - ((self.mana_bar_width/self.max_mp)*(self.max_mp - self.mana_points)))
        pygame.draw.rect(display, BLACK,
                         (4, 29, self.mana_bar_width+2, 12), 1)
        pygame.draw.rect(display, BLUE,
                         (5, 30, mana_bar_width, 10))

        x = 5
        y = 45
        for effect in self.effects:
            pygame.draw.rect(display, BLACK,
                             (x-1, y, self.effect_icon_width+2, self.effect_icon_height), 1)
            display.blit(effect, (x, y))
            x += 40

    def draw_cooldowns(self, display, font):
        if get_cooldown_ready(self.fireball_time, self.cooldowns['range'],  self.update_time):
            pygame.draw.circle(display, GREEN, (25, SCREEN_SIZE[1]-25), 20)
            display.blit(self.fireball_icon, (5, SCREEN_SIZE[1]-35))
        else:
            pygame.draw.circle(display, RED, (25, SCREEN_SIZE[1]-25), 20)
            draw_text(str(abs(self.update_time-self.fireball_time-self.cooldowns['range'])//1000), font, WHITE,
                      display, 25, SCREEN_SIZE[1]-40)

        if get_cooldown_ready(self.melee_attack_time, self.cooldowns['melee'], self.update_time):
            pygame.draw.circle(display, GREEN, (70, SCREEN_SIZE[1]-25), 20)
            display.blit(self.staff_icon, (65, SCREEN_SIZE[1]-35))
        else:
            pygame.draw.circle(display, RED, (70, SCREEN_SIZE[1]-25), 20)
            draw_text(str(abs(self.update_time-self.melee_attack_time-self.cooldowns['melee'])//1000), font, WHITE,
                      display, 70, SCREEN_SIZE[1]-40)

        if get_cooldown_ready(self.lightning_time, self.cooldowns['lightning'], self.update_time):
            pygame.draw.circle(display, GREEN, (115, SCREEN_SIZE[1]-25), 20)
            display.blit(self.lightning_icon, (100, SCREEN_SIZE[1]-35))
        else:
            pygame.draw.circle(display, RED, (115, SCREEN_SIZE[1]-25), 20)
            draw_text(str(abs(self.update_time-self.lightning_time-self.cooldowns['lightning'])//1000), font, WHITE,
                      display, 115, SCREEN_SIZE[1]-40)

    def hit(self, damage):
        if self.invulnerability:
            return
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

    def update_animation(self, new_entities):
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

        if (self.action == int(Animation_type.Throwing_in_The_Air) or self.action == int(Animation_type.Run_Throwing)) and self.frame_index == 2 and self.ready_to_fire:
            if self.casting == 'fireball':
                self.fire()
                self.ready_to_fire = False
            elif self.casting == 'lightning':
                self.cast_lightning()
                self.ready_to_fire = False

        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.death_screen_ready = True
            elif self.action == int(Animation_type.Slashing) or self.action == int(Animation_type.Hurt):
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
        if len(collision_list):
            for col in collision_list:
                if not col.state == col.states['APPEARING']:
                    col.hit(self.melee_damage)
                    bonk_sound.play()
            self.regenerate_mana(20)

    def fire(self):
        random.choice([fireball_cast_sound, fireball_cast2_sound]).play()
        self.fireball_time = self.update_time
        if self.facing_positive:
            direction = 1
            projectile = Projectile(
                Vector2(self.hitbox.x + self.hitbox.w, self.hitbox.centery), direction, Vector2(0, 0), 1, self.projectile_damage, self.projectile_speed)
        else:
            direction = -1
            projectile = Projectile(
                Vector2(self.hitbox.x, self.hitbox.centery), direction, Vector2(0, 0), 1, self.projectile_damage, self.projectile_speed)

        self.projectiles.append(projectile)
        self.mana_points -= self.mana_costs['fireball']
        self.ready_to_fire = False

    def cast_lightning(self):
        random.choice([fireball_cast_sound, fireball_cast2_sound]).play()
        self.lightning_time = self.update_time
        if self.facing_positive:
            direction = 1
            lightning = Lightning(
                Vector2(self.hitbox.x, self.hitbox.centery - 320), 'lightning', 0, direction, Vector2(self.rect.width, self.rect.height))
        else:
            direction = -1
            lightning = Lightning(
                Vector2(self.hitbox.x - 250 + self.rect.w, self.hitbox.centery - 320), 'lightning', 0, direction, Vector2(self.rect.width, self.rect.height))

        lightning.ready = True
        self.lightnings.append(lightning)
        self.mana_points -= self.mana_costs['lightning']
        self.ready_to_fire = False

    def state_running_attacking(self, new_entities):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Slashing)
            self.melee_attack(new_entities)

    def state_running_firing(self):
        if self.init_state:
            self.init_state = False
            self.set_action(Animation_type.Run_Throwing)

    def regenerate_mana(self, amount):
        if amount + self.mana_points >= self.max_mp:
            self.mana_points = self.max_mp
        if amount + self.mana_points < self.max_mp:
            self.mana_points += amount
