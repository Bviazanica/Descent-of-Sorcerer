import random
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
Vector2 = pygame.math.Vector2


class Boss():
    def __init__(self):
        # image
        self.images = []
        self.boss_img = pygame.image.load(
            'data/images/entities/bosses/robot.png').convert_alpha()
        bossImg = pygame.transform.scale(self.boss_img, (72, 128))
        self.images.append(self.boss_img)
        self.image = self.images[0]

        # rect
        self.rect = self.image.get_rect(width=(75), height=(100))

        self.rect.center = 200, 400

        self.type = 'Boss'

        # hitbox
        self.hitbox = pygame.Rect(
            self.rect.x, self.rect.y, 75, 100)

        self.cooldowns = {'summon': 15000, 'whirlwind': 10000, 'orbs': 5000}

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

                elif projectile.rect.x > 1500 or projectile.rect.x < -380:
                    self.projectiles.pop(self.projectiles.index(projectile))

                else:
                    projectile.update(time)

        self.hitbox[0] = self.rect.x + 10
        self.hitbox[1] = self.rect.y + 35

    def draw(self, display, offset_x, offset_y):
        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))

        pygame.draw.rect(display, (255, 0, 0), [
                         self.hitbox[0] - offset_x, self.hitbox[1] - offset_y, 75, 100], 2)

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
