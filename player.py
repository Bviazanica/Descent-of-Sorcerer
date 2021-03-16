import os
import sys
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
from data.gameobjects.vector2 import Vector2


class Player():
    def __init__(self):
        self.type = 'player'

        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ['Idle', 'Running', ]
        # load all images for the players
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'data/images/entities/{self.type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'data/images/entities/{self.type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (64, 128))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        # hitbox
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        # direction
        self.left = False
        self.right = True

        self.moving_left = False
        self.moving_right = True

        # cooldowns
        self.cooldowns = {'melee': 2000, 'range': 2000}

        # attack damage
        self.shoot_damage = 10
        self.melee_damage = 200

        # speed
        self.speed = 250

        # projectiles
        self.projectiles = []

        # healthpoints
        self.health_points = 2000
        self.max_health = 2000

        # camera borders
        self.top_border, self.bottom_border = -268, 746
        self.left_border, self.right_border = -380, 1500
        self.player_border_min_y, self.player_border_max_y = 120, 640

    # update position
    def update(self, display, time, movement, entities):
        if self.moving_left or self.moving_right:
            self.set_action(1)
        else:
            self.set_action(0)

        self.update_animation()
        new_entities = new_list_without_self(self, entities)
        if self.projectiles:
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

        self.rect, collisions = self.move(
            self.rect, movement, new_entities, time)

        self.hitbox = pygame.Rect(
            (self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()))

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

        if(self.rect.x < self.left_border):
            self.rect.x = self.left_border
        if(self.rect.x > self.right_border - self.rect.width):
            self.rect.x = self.right_border - self.rect.width

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

        if(self.rect.y < self.player_border_min_y):
            self.rect.y = self.player_border_min_y
        if(self.rect.y > self.player_border_max_y - self.rect.height):
            self.rect.y = self.player_border_max_y - self.rect.height

        return self.rect, collision_types

    # draw player to canvas
    def draw(self, display, offset_x, offset_y, player):
        if(self.projectiles):
            for projectile in self.projectiles:
                projectile.draw(display, offset_x, offset_y)

        display.blit(self.image, (self.rect.x -
                                  offset_x, self.rect.y - offset_y))
        self.hitbox = pygame.Rect(
            (self.rect.x - offset_x, self.rect.y - offset_y, self.image.get_width(), self.image.get_height()))
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def fire(self, display, new_entities, offset_x, offset_y):
        if self.right:
            direction = 1
        else:
            direction = -1
        projectile = Projectile(
            Vector2(self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2), direction, Vector2(0, 0), 'player')
        self.projectiles.append(projectile)

    def melee_attack(self, display, new_entities, offset_x, offset_y):
        if self.right:
            direction = 1
        else:
            direction = -1
        attack = pygame.Rect(self.rect.x + (self.rect.w*direction), self.rect.y,
                             36, 64)
        collision_list = check_collision(attack, new_entities)
        for col in collision_list:
            col.hit(self.melee_damage)

    def hit(self, damage):
        self.health_points -= damage

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if time passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # out of images - resets
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def set_action(self, new_action):
        # check if the new action != previous
        if new_action != self.action:
            self.action = new_action
            # update animation from start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
