import random
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
Vector2 = pygame.math.Vector2


class Boss():
    def __init__(self, x, y):
        self.type = 'boss'

        # id
        self.entity_id = 1

        self.is_alive = True

        # animations
        self.animation_list = entities_animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3

        # id for animations
        self.entity_id = 1

        # flip image based on direction
        self.flip = False

        # image properties
        self.image = self.animation_list[self.action][self.frame_index]
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # rect
        self.rect = self.image.get_rect(width=90, height=125)
        self.rect.center = (x, y)

        # hitbox
        self.hitbox_x_offset = 50
        self.hitbox_y_offset = 45

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        # cooldown on abilities
        self.cooldowns = {'summon': 5000, 'whirlwind': 10000, 'orbs': 2000}
        self.whirlwind_activation_time = self.orbs_activation_time = self.summon_activation_time = -10000
        # speed
        self.speed = 200
        # health points & bars properties
        self.max_hp = 300
        self.health_points = 300

        self.hp_bar_width = self.rect.w

        self.update_time = 0
        self.animation_time = 0
        self.timeout = 0
        self.projectiles = []

        # desired location vector
        self.desired = Vector2(0, 0)
        self.desired_appear = Vector2(0, 0)

        # states
        self.states = {'HURTING': 'HURTING', 'DYING': 'DYING', 'SUMMONING': 'SUMMONING',
                       'ATTACKING': 'ATTACKING', 'IDLING': 'IDLING', 'FIRING': 'FIRING', 'APPEARING': 'APPEARING'}

        self.state = self.states['APPEARING']
        self.init_state = True
        self.last_state = ''

        self.ready_to_attack = False
        self.ready_to_fire = True
        self.entities_summoned = False

    def update(self, player, time_passed, tick, movement, entities, Mob, stage, wave_number):
        self.update_time = time_passed
        new_entities = new_list_without_self(self, entities)
        self.desired = (
            player.hitbox.center - Vector2(self.hitbox.centerx, self.hitbox.centery))
        self.update_animation(player, Mob, wave_number)

        if self.is_alive:
            if self.desired[0] <= 0:
                self.flip = True
            else:
                self.flip = False

            if self.state == 'APPEARING':
                self.go_to = Vector2(
                    self.desired_appear.x - self.rect.centerx, self.desired_appear.y - self.rect.centery)
                self.set_action(Animation_type.Falling)
                if self.go_to.x <= 0:
                    self.flip = True
                else:
                    self.flip = False
                if abs(self.go_to.y) > 5:
                    self.go_to.normalize_ip()
                    self.rect.centery += self.go_to.y * self.speed * tick
                    self.hitbox.x = self.rect.x + self.hitbox_x_offset
                    self.hitbox.y = self.rect.y + self.hitbox_y_offset
                else:
                    self.state = self.states['IDLING']
                    self.set_action(Animation_type.Walking)
                    self.init_state = True
            else:
                if self.init_state and self.state != self.states['DYING']:
                    if is_close(self.hitbox, player.hitbox, 200) and self.update_time - self.whirlwind_activation_time > self.cooldowns['whirlwind'] and not self.ready_to_attack:
                        self.ready_to_attack = True
                        self.timeout = self.update_time
                    if self.timeout != 0 and self.update_time - self.timeout > 2000 and self.ready_to_attack:

                        self.timeout = 0
                        self.state = self.states['ATTACKING']
                if not self.ready_to_attack and self.init_state:
                    if get_entity_count(new_entities, 'mob') == 0 and self.update_time - self.summon_activation_time > self.cooldowns['summon']:
                        self.state = self.states['SUMMONING']
                    elif self.update_time - self.orbs_activation_time > self.cooldowns['orbs']:
                        self.frame_index = 0
                        self.state = self.states['FIRING']

                if self.init_state:
                    if self.state == 'IDLING':
                        self.set_action(Animation_type.Idle_Blinking)
                    elif self.state == 'HURTING':
                        self.init_state = False
                        self.set_action(Animation_type.Hurt)
                    elif self.state == 'SUMMONING':
                        self.summon_activation_time = self.update_time
                        self.init_state = False
                        self.set_action(Animation_type.Summoning)
                    elif self.state == 'ATTACKING':
                        self.whirlwind_activation_time = self.update_time
                        self.init_state = False
                        self.set_action(
                            Animation_type.Slashing_in_The_Air)
                    elif self.state == 'FIRING':
                        self.orbs_activation_time = self.update_time
                        self.init_state = False
                        self.set_action(
                            Animation_type.Throwing_in_The_Air)
                    elif self.state == 'APPEARING':
                        self.init_state = False
                        self.set_action(Animation_type.Walking)

                    check_boundaries_for_x(self)
                    self.hitbox.x = self.rect.x + self.hitbox_x_offset
                    check_boundaries_for_y(self)
                    self.hitbox.y = self.rect.y + self.hitbox_y_offset

        if(self.projectiles):
            for projectile in self.projectiles:
                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list):
                    for col in collision_list:
                        col.hit(projectile.damage)
                    self.projectiles.pop(self.projectiles.index(projectile))

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER or projectile.rect.y < CAMERA_TOP or projectile.rect.y > CAMERA_BOTTOM:
                    self.projectiles.pop(self.projectiles.index(projectile))

                else:
                    projectile.update(self.update_time, tick, [], False)

    def draw(self, display, offset_x, offset_y, player):
        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.rect.width, self.rect.height], 2)

        # healthbar
        pygame.draw.rect(display, (255, 0, 0),
                         (self.hitbox.x - offset_x, self.hitbox.y - 15 - offset_y, self.hp_bar_width, 10))
        if self.is_alive:
            pygame.draw.rect(display, (0, 200, 0),
                             (self.hitbox.x - offset_x, self.hitbox.y - 15 - offset_y, self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)), 10))

        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)

    def fire(self, target):
        throw_sound.play()
        self.desired = target - \
            Vector2(self.hitbox.centerx, self.hitbox.centery)
        self.desired.normalize_ip()
        if self.desired[0] <= 0:
            projectile = Projectile(
                (self.hitbox.x, self.hitbox.centery), 1, self.desired, 0, 15)
        else:
            projectile = Projectile(
                (self.hitbox.x + self.hitbox.width, self.hitbox.centery), 1, self.desired, 0, 15)
        self.projectiles.append(projectile)

    def whirlwind(self, player):
        if is_close(self.hitbox, player.hitbox, 200):
            self.damage = 20
            player.hit(self.damage)

    def heal(self, heal_amount):
        self.health_points += heal_amount

    def hit(self, damage):
        if self.health_points - damage <= 0:
            self.is_alive = False
            self.state = self.states['DYING']
            self.set_action(Animation_type.Dying)
            self.init_state = False
            self.health_points = 0
            boss_hurt_sound.play()
        elif self.is_alive and self.state == self.states['HURTING']:
            self.init_state = True
            self.frame_index = 0
            self.init_state = False
            self.health_points -= damage
        elif self.is_alive and self.state != self.states['DYING']:
            self.init_state = True
            self.state = self.states['HURTING']
            self.health_points -= damage

    def get_summoned_entities(self):
        return self.new_entities

    def update_animation(self, player, Mob, wave_number):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Kicking) or self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 30

        if self.action == int(Animation_type.Throwing_in_The_Air):
            ANIMATION_COOLDOWN = 20

        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1
        # out of images - resets

        if self.action == int(Animation_type.Slashing_in_The_Air) and self.frame_index == len(self.animation_list[self.action])/2 and self.ready_to_attack:
            self.whirlwind(player)
            self.ready_to_attack = False
        if self.action == int(Animation_type.Throwing_in_The_Air) and self.frame_index == 2 and self.ready_to_fire:
            self.fire(player.hitbox.center)
            self.ready_to_fire = False
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.init_state = True
            elif self.action == int(Animation_type.Hurt):
                self.frame_index = 0
                self.init_state = True
                self.state = self.states['IDLING']
            elif self.action == int(Animation_type.Slashing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
            elif self.action == int(Animation_type.Throwing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
                self.ready_to_fire = True
            elif self.action == int(Animation_type.Summoning):
                self.new_entities = summon(
                    Mob, self.hitbox.centerx + random.choice(
                        [randint(-200, -50), randint(130, 200)]), 50, 3, wave_number, 0, False)
                self.entities_summoned = True
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
            self.animation_time = self.update_time
