import random
import pygame
from data.utility import *
from pygame.locals import *
from data.projectile import Projectile
from data.objects.items.item import Item
Vector2 = pygame.math.Vector2


class Potion(Item):
    def __init__(self, points_to_restore, name, pos, w, h):
        self.points_to_restore = points_to_restore
        super(Potion, self).__init__(name, pos, w, h)

    def heal(self, target, items):
        if target.health_points == target.max_hp:
            pass
        else:
            if target.health_points + self.points_to_restore >= target.max_hp:
                target.health_points = target.max_hp
            elif target.health_points + self.points_to_restore < target.max_hp:
                target.health_points += self.points_to_restore
        items.pop(items.index(self))

    def regenerate_mana(self, target, items):
        target.regenerate_mana(20)
        items.pop(items.index(self))

    def boost(self, target, items, time):
        target.boosted_timer = time
        if target.power_icon in target.effects:
            pass
        else:
            target.effects.append(target.power_icon)
            target.boosted = True
        items.pop(items.index(self))

    def invulnerability(self, target, items, time):
        target.invulnerability_timer = time
        if target.invulnerability_icon in target.effects:
            pass
        else:
            target.effects.append(target.invulnerability_icon)
            target.invulnerability = True
        items.pop(items.index(self))
