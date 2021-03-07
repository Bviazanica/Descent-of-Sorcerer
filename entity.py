import pygame
from pygame.locals import *


def check_collision(rect, obj_list):
    collisions = []
    for obj in obj_list:
        if rect.colliderect(obj.hitbox):
            collisions.append(obj)
    return collisions
