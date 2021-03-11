import math
import pygame
from pygame.locals import *
from data.globals.globals import *


def check_collision(rect, obj_list):
    collisions = []
    for obj in obj_list:
        if rect.colliderect(obj.hitbox):
            collisions.append(obj)
    return collisions


def is_close(object1, object2, distance):
    return math.hypot(object2.centerx-object1.centerx, object2.centery-object1.centery) < float(distance)
