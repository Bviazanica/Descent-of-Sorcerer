import random
import pygame
from data.utility import *
from pygame.locals import *
from data.projectile import Projectile
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
        self.cooldowns = {'summon': 17000,
                          'whirlwind': 10000, 'orbs': 1700}
        self.whirlwind_activation_time = self.orbs_activation_time = self.summon_activation_time = -100000
        # speed
        self.speed = 200
        # health points & bars properties
        self.max_hp = 250
        self.health_points = 250

        self.hp_bar_width = 300

        self.whirlwind_damage = 30
        self.projectile_damage = 25
        self.projectile_speed = 200

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
        self.init_state = False

        self.ready_to_attack = False
        self.ready_to_fire = True
        self.entities_summoned = False
        self.spawn_mobs_number = 3

    def update(self, player, time_passed, tick, movement, entities, Mob, stage, wave_number, start_upgrade_after_wave):
        self.update_time = time_passed
        new_entities = new_list_without_self(self, entities)
        self.desired = (
            player.hitbox.center - Vector2(self.hitbox.centerx, self.hitbox.centery))
        self.update_animation(player, Mob, wave_number,
                              start_upgrade_after_wave)

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
                    self.set_action(Animation_type.Idle_Blinking)
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
                    elif self.state == 'SUMMONING':
                        self.init_state = False
                        self.set_action(Animation_type.Summoning)
                    elif self.state == 'ATTACKING':
                        self.init_state = False
                        self.set_action(
                            Animation_type.Slashing_in_The_Air)
                    elif self.state == 'FIRING':
                        self.init_state = False
                        self.set_action(
                            Animation_type.Throwing_in_The_Air)

                    check_boundaries_for_x(self)
                    self.hitbox.x = self.rect.x + self.hitbox_x_offset
                    check_boundaries_for_y(self)
                    self.hitbox.y = self.rect.y + self.hitbox_y_offset

        if(self.projectiles):
            for projectile in self.projectiles:

                collision_list = check_collision(
                    projectile.rect, new_entities)
                if len(collision_list) and not projectile.destroy:
                    projectile.destroy = True
                    for col in collision_list:

                        col.hit(projectile.damage)
                    projectile.update(self.update_time, tick,
                                      self.projectiles)

                elif projectile.rect.x > RIGHT_BORDER or projectile.rect.x < LEFT_BORDER or projectile.rect.y < CAMERA_TOP or projectile.rect.y > CAMERA_BOTTOM:
                    self.projectiles.pop(self.projectiles.index(projectile))

                else:
                    projectile.update(self.update_time, tick, self.projectiles)

        # print(
        #     f'SPEED: {self.projectile_speed} DMG: {self.projectile_damage} CD: {self.cooldowns["orbs"]}')

    def draw(self, display, offset_x, offset_y, player):

        display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -
                                                                           offset_x, self.rect.y - offset_y))

        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)
        # healthbar
        pygame.draw.rect(display, (0, 0, 0),
                         (SCREEN_SIZE[0] - 6 - self.hp_bar_width, 4, self.hp_bar_width + 2, 22), 1)
        healthbar_width = int(
            self.hp_bar_width - ((self.hp_bar_width/self.max_hp)*(self.max_hp - self.health_points)))
        if self.is_alive:
            pygame.draw.rect(display, (255, 0, 0),
                             (SCREEN_SIZE[0] - 5 - healthbar_width, 5, healthbar_width, 20))

        draw_text('Golem', font_gothikka_bold, WHITE,
                  display, SCREEN_SIZE[0]-35, 25)

    def fire(self, target):
        throw_sound.play()
        self.desired = target - \
            Vector2(self.hitbox.centerx, self.hitbox.centery)
        self.desired.normalize_ip()
        if self.desired[0] <= 0:
            projectile = Projectile(
                (self.hitbox.x, self.hitbox.centery), -1, self.desired, 0, self.projectile_damage, self.projectile_speed)
        else:
            projectile = Projectile(
                (self.hitbox.x + self.hitbox.width, self.hitbox.centery), 1, self.desired, 0, self.projectile_damage, self.projectile_speed)
        self.projectiles.append(projectile)

    def whirlwind(self, player):
        if is_close(self.hitbox, player.hitbox, 200):
            player.hit(self.whirlwind_damage)

    def heal(self, heal_amount):
        if self.health_points + heal_amount <= self.max_hp:
            self.health_points += heal_amount
        elif self.health_points + heal_amount > self.max_hp:
            self.health_points = self.max_hp

    def hit(self, damage):
        if self.health_points - damage <= 0 and self.state != self.states['DYING']:
            self.is_alive = False
            self.state = self.states['DYING']
            self.set_action(Animation_type.Dying)
            self.init_state = False
            self.health_points = 0
            boss_hurt_sound.play()
        if self.is_alive:
            if self.state == self.states['HURTING'] or self.state == self.states['ATTACKING']:
                self.health_points -= damage
            elif self.state != self.states['DYING']:
                self.state = self.states['HURTING']
                self.set_action(Animation_type.Hurt)
                self.frame_index = 0
                self.init_state = False
                self.health_points -= damage

    def get_summoned_entities(self):
        return self.new_entities

    def update_animation(self, player, Mob, wave_number, start_upgrade_after_wave):
        ANIMATION_COOLDOWN = 50
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if self.action == int(Animation_type.Slashing_in_The_Air) or self.action == int(Animation_type.Hurt):
            ANIMATION_COOLDOWN = 30

        if self.action == int(Animation_type.Throwing_in_The_Air):
            ANIMATION_COOLDOWN = 20

        if self.update_time - self.animation_time > ANIMATION_COOLDOWN:
            self.animation_time = self.update_time
            self.frame_index += 1
        # out of images - resets

        if self.action == int(Animation_type.Slashing_in_The_Air) and self.frame_index == len(self.animation_list[self.action])/2 and self.ready_to_attack:
            self.whirlwind_activation_time = self.update_time
            self.whirlwind(player)
            self.ready_to_attack = False
        if self.action == int(Animation_type.Throwing_in_The_Air) and self.frame_index == 2 and self.ready_to_fire:
            self.orbs_activation_time = self.update_time
            self.fire(player.hitbox.center)
            self.ready_to_fire = False
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == int(Animation_type.Dying):
                self.frame_index = len(self.animation_list[self.action]) - 1
                self.init_state = True
            elif self.action == int(Animation_type.Hurt):
                self.state = self.states['IDLING']
                self.frame_index = 0
                self.init_state = True
            elif self.action == int(Animation_type.Slashing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
            elif self.action == int(Animation_type.Throwing_in_The_Air):
                self.state = self.states['IDLING']
                self.init_state = True
                self.ready_to_fire = True
            elif self.action == int(Animation_type.Summoning):
                self.summon_activation_time = self.update_time
                self.new_entities = summon(
                    Mob, self.hitbox.centerx + random.choice(
                        [randint(-200, -50), randint(130, 200)]), 50, self.spawn_mobs_number, wave_number, 0, False, start_upgrade_after_wave)
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
