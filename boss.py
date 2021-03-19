import random
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
Vector2 = pygame.math.Vector2


class Boss():
    def __init__(self):
        self.type = 'boss'

        self.entity_id = 1
        self.is_alive = True

        self.flip = False
        self.animation_list = animation_list[self.entity_id]
        self.frame_index = 0
        self.action = 3
        self.update_time = pygame.time.get_ticks()

        self.image = self.animation_list[self.action][self.frame_index]

        # image properties
        self.image_height = self.image.get_height()
        self.image_width = self.image.get_width()
        # rect
        self.rect = self.image.get_rect(width=90, height=125)

        self.rect.center = 200, 200

        self.hitbox_x_offset = 50
        self.hitbox_y_offset = 45

        self.hitbox = pygame.Rect(
            (self.rect.x + self.hitbox_x_offset, self.rect.y + self.hitbox_y_offset, self.rect.width, self.rect.height))

        print(f'{self.rect}')

        # hitbox

        self.cooldowns = {'summon': 15000, 'whirlwind': 10000, 'orbs': 5000}

        self.init_state = True
        # speed
        self.speed = 200
        # healthpoints
        self.max_hp = 300
        self.health_points = 300

        self.hp_bar_width = self.rect.w

        self.projectiles = []

        self.desired = Vector2(0, 0)

        self.ready = True

    def update(self, display, time, movement, entities):
        new_entities = new_list_without_self(self, entities)
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

        if self.rect.x + self.hitbox_x_offset < LEFT_BORDER:
            self.rect.x = LEFT_BORDER - self.hitbox_x_offset
        if(self.rect.x + self.rect.width + self.hitbox_x_offset > RIGHT_BORDER):
            self.rect.x = RIGHT_BORDER - self.rect.width - self.hitbox_x_offset
        self.hitbox.x = self.rect.x + self.hitbox_x_offset
        self.hitbox[0] = self.rect.x + 50
        if self.rect.y + self.image_height - self.hitbox_y_offset < TOP_BORDER:
            self.rect.y = TOP_BORDER - self.image_height + self.hitbox_y_offset
        if self.rect.y + self.image_height - self.hitbox_y_offset > BOTTOM_BORDER:
            self.rect.y = BOTTOM_BORDER - self.image_height + self.hitbox_y_offset
        self.hitbox[1] = self.rect.y + 45

    def draw(self, display, offset_x, offset_y, player):
        display.blit(self.image, (self.rect.x -
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

    def shoot(self, target, time):
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
        self.health_points -= damage
