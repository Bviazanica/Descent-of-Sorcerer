import os
import math
import pygame
from pygame import mixer
from random import randint
from pygame.locals import *
from data.globals.globals import *


def check_collision(rect, obj_list):
    collisions = []
    for obj in obj_list:
        if rect.colliderect(obj.hitbox):
            collisions.append(obj)
    return collisions


def new_list_without_self(self, object_list):
    new_list = []
    new_list = [x for x in object_list if not x.type == self.type]
    return new_list


def is_close(object1, object2, distance):
    return math.hypot(object2.centerx-object1.centerx, object2.centery-object1.centery) < float(distance)


def summon(object, x, y, number):
    mobs = []
    for mob in range(number):
        mob = object(x, y)
        mobs.append(mob)
        y += 125
    return mobs


def check_boundaries_for_x(self):
    if self.rect.x + self.hitbox_x_offset < LEFT_BORDER:
        self.rect.x = LEFT_BORDER - self.hitbox_x_offset
    if(self.rect.x + self.rect.width + self.hitbox_x_offset > RIGHT_BORDER):
        self.rect.x = RIGHT_BORDER - self.rect.width - self.hitbox_x_offset


def check_boundaries_for_y(self):
    if self.rect.y + self.image_height - self.hitbox_y_offset < TOP_BORDER:
        self.rect.y = TOP_BORDER - self.image_height + self.hitbox_y_offset
    if self.rect.y + self.image_height - self.hitbox_y_offset > BOTTOM_BORDER:
        self.rect.y = BOTTOM_BORDER - self.image_height + self.hitbox_y_offset


def get_entity_count(entities, entity_type):
    entity_count = 0
    for entity in entities:
        if entity.type == entity_type:
            entity_count += 1
    return entity_count


def get_entities(entities, entity_type):
    new_entities = []
    for entity in entities:
        if entity.type == entity_type:
            new_entities.append(entity)
    return new_entities


def get_cooldown_ready(last_used_time, cooldown_time, time_passed):
    time = time_passed
    if time - last_used_time > cooldown_time:
        return True
    else:
        return False


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.midtop = (x, y)
    surface.blit(textobj, textrect)


def load_entity_animations():
    animation_types = ['Dying', 'Hurt', 'Idle', 'Idle Blinking', 'Kicking', 'Run Slashing', 'Run Throwing',
                       'Running', 'Slashing', 'Slashing in The Air', 'Throwing', 'Throwing in The Air', 'Walking', 'Summoning']
    entity_types = ['player', 'boss', 'mob']

    list_of_loaded_animations = []
    for entity_type in entity_types:
        entity_animations = []
        if entity_type == 'player':
            w = h = 120
        elif entity_type == 'mob':
            w = h = 100
        elif entity_type == 'boss':
            w = h = 200
        # load all images for the players
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            if os.path.isdir(f'data/images/entities/{entity_type}/{animation}'):
                num_of_frames = len(os.listdir(
                    f'data/images/entities/{entity_type}/{animation}/new'))

                for i in range(num_of_frames):
                    # print(f'{entity_type} & {animation} - {i}')
                    img = pygame.image.load(
                        f'data/images/entities/{entity_type}/{animation}/new/{i}.png')
                    img = pygame.transform.scale(img, (w, h))
                    temp_list.append(img)

                entity_animations.append(temp_list)
            else:
                entity_animations.append([])

        list_of_loaded_animations.append(entity_animations)

    return list_of_loaded_animations


def load_projectile_animations():
    animation_types = ['rock', 'fireball']
    projectile_animations = []
    for animation in animation_types:
        temp_list = []
        if os.path.isdir(f'data/images/projectiles/{animation}'):
            num_of_frames = len(os.listdir(
                f'data/images/projectiles/{animation}'))

            for i in range(num_of_frames):
                # print(f'{entity_type} & {animation} - {i}')
                img = pygame.image.load(
                    f'data/images/projectiles/{animation}/{i}.png')
                if animation == 'fireball' and i < 5:
                    img = pygame.transform.scale(img, (55, 31))
                else:
                    img = pygame.transform.scale(img, (30, 43))
                temp_list.append(img)
            projectile_animations.append(temp_list)
    return projectile_animations


entities_animation_list = load_entity_animations()
projectiles_animation_list = load_projectile_animations()
