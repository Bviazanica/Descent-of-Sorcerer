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
