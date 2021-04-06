import random
import pygame
from data.utility import *
from pygame.locals import *
from data.projectile import Projectile
from data.objects.items.item import Item
Vector2 = pygame.math.Vector2


class Potion(Item):
    def __init__(self, name, pos, w, h):
        super(Potion, self).__init__(name, pos, w, h)

    def heal(self, target, items, amount):
        if target.health_points == target.max_hp:
            return
        else:
            if target.health_points + amount >= target.max_hp:
                target.health_points = target.max_hp
            elif target.health_points + amount < target.max_hp:
                target.health_points += amount
        items.pop(items.index(self))
        potion_sound.play()

    def regenerate_mana(self, target, items, amount):
        target.regenerate_mana(amount)
        items.pop(items.index(self))
        potion_sound.play()

    def boost(self, target, items, time):
        target.boosted_timer = time

        if target.power_icon in target.effects:
            target.boosted_stacks += 1
            boost_attacks([target.projectile_damage, target.melee_damage,
                           target.lightning_damage, target.decoy_damage], target.boosted_stacks, target)
        else:
            target.boosted_stacks = 1
            target.boosted_attacks_by = [
                target.projectile_damage, target.melee_damage, target.lightning_damage, target.decoy_damage]
            boost_attacks([target.projectile_damage, target.melee_damage,
                           target.lightning_damage, target.decoy_damage], target.boosted_stacks, target)
            target.effects.append(target.power_icon)
            target.boosted = True
        potion_sound.play()
        items.pop(items.index(self))

    def invulnerability(self, target, items, time):
        target.invulnerability_timer = time
        if target.invulnerability_icon in target.effects:
            pass
        else:
            target.effects.append(target.invulnerability_icon)
            target.invulnerability = True
        items.pop(items.index(self))
        potion_sound.play()
