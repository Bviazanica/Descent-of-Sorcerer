import random
import pygame
from utility import *
from pygame.locals import *
from projectile import Projectile
from data.objects.items.item import Item
Vector2 = pygame.math.Vector2


class Potion(Item):
    def __init__(self, points_to_restore, name, pos, w, h):
        self.points_to_restore = points_to_restore
        super(Potion, self).__init__(name, pos, w, h)

    def heal(self, target, items):
        if target.health_points == target.max_hp:
            return
        else:
            potion_sound.play()
            if target.health_points + self.points_to_restore >= target.max_hp:
                target.health_points = target.max_hp
            elif target.health_points + self.points_to_restore < target.max_hp:
                target.health_points += self.points_to_restore
            items.pop(items.index(self))
