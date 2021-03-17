import os
import math
import pygame
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


def load_animations(entity_type, w, h):
    animation_types = ['Dying', 'Hurt', 'Idle', 'Idle Blinking', 'Kicking', 'Run Slashing', 'Run Throwing',
                       'Running', 'Slashing', 'Slashing in The Air', 'Throwing', 'Throwing in The Air', 'Walking']
    list_of_loaded_animations = []
    # load all images for the players
    for animation in animation_types:
        # reset temporary list of images
        temp_list = []
        # count number of files in the folder
        if os.path.isdir(f'data/images/entities/{entity_type}/{animation}'):
            num_of_frames = len(os.listdir(
                f'data/images/entities/{entity_type}/{animation}'))

            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'data/images/entities/{entity_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (w, h))
                temp_list.append(img)
            list_of_loaded_animations.append(temp_list)
        else:
            print(f'skipped {animation}')

    return list_of_loaded_animations
