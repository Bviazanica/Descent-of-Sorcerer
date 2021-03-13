import math
import pygame
from random import randint
from pygame.locals import *
from data.globals.globals import *


def check_collision(rect, obj_list, skip):
    collisions = []
    for obj in obj_list:
        if obj.type == skip:
            continue
        elif rect.colliderect(obj.hitbox):
            collisions.append(obj)
    return collisions


def is_close(object1, object2, distance):
    return math.hypot(object2.centerx-object1.centerx, object2.centery-object1.centery) < float(distance)


def summon(object, x, y, number):
    creatures = []
    for creature in range(number):
        creature = object(x, y)
        creatures.append(creature)
        y += 125
    return creatures
