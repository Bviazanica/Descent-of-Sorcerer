# Setup python
import os
import sys
import pygame
import random
from data import *
from utility import *
from boss import Boss
from enemy import Enemy
from player import Player
from pygame.locals import *
from data.camera.camera import *
from data.globals.globals import *
from data.gameobjects.vector2 import Vector2
from data.objects.items.potion import Potion

# window & canvas
window = pygame.display.set_mode(SCREEN_SIZE)
canvas = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))

# setup
clock = pygame.time.Clock()
pygame.init()

# Title
pygame.display.set_caption("Game")

# background
background = pygame.image.load(
    'data/images/backgrounds/background.png').convert()
bgWidth = background.get_width()
bgHeight = background.get_height()

# entities
entities = []
items = []
mobs = []

player = Player()
entities.append(player)
boss = Boss()
entities.append(boss)

# camera & methods
camera = Camera(player)
follow = Follow(camera, player)
border = Border(camera, player)
auto = Auto(camera, player)
camera.setmethod(border)

running = True
current_time = 0

# player cooldowns
attack_with_delay = USEREVENT

pygame.time.set_timer(attack_with_delay, 2000)
melee_attack_time = whirlwind_activation_time = range_attack_time = -100000

# Game Loop
while running:
    canvas.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # frame interval
    time_passed = clock.tick(FPS)
    time_passed_seconds = time_passed / 1000.0
    pressed_keys = pygame.key.get_pressed()
    movement = Vector2(0, 0)

    if player.health_points <= 0:
        player.is_alive = False
        player.state = player.states['DYING']
    else:
        # movement
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            movement.x = -1
            player.facing_positive = False
        elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            movement.x = +1
            player.facing_positive = True
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            movement.y = -1
        elif pressed_keys[K_DOWN] or pressed_keys[K_s]:
            movement.y = +1

        if (pressed_keys[K_d] or pressed_keys[K_a] or pressed_keys[K_s] or pressed_keys[K_w]
                or pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_UP] or pressed_keys[K_DOWN]) and player.init_state and player.state != player.states['HURTING']:
            player.state = player.states['RUNNING']

        if pressed_keys[K_SPACE] and current_time - range_attack_time > player.cooldowns['range']:
            range_attack_time = pygame.time.get_ticks()
            if player.state == 'RUNNING':
                player.state = player.states['RUNNING-FIRING']
            else:
                player.state = player.states['FIRING']

        if pressed_keys[K_f] and current_time - melee_attack_time > player.cooldowns['melee']:
            melee_attack_time = pygame.time.get_ticks()
            if player.state == 'RUNNING':
                player.state = player.states['RUNNING-ATTACKING']
            else:
                player.state = player.states['ATTACKING']

        if not pressed_keys.count(1) and player.state != player.states['HURTING'] and player.state != player.states['DYING']:
            player.state = player.states['IDLING']

        movement.normalize()

    enemies_count = 0

    for entity in entities:
        if entity.type == 'Mob':
            enemies_count += 1

    if enemies_count == 0:
        mobs = summon(Enemy, 500, 200, 1)
        entities.extend(mobs)

    for entity in entities:
        if entity.type == 'player':
            entity.update(canvas, time_passed_seconds, movement,
                          entities)
        elif entity.type == 'boss':
            entity.update(canvas, time_passed_seconds, movement,
                          entities)
        elif entity.type == 'Mob':
            entity.update(time_passed_seconds, player, current_time, mobs)
        if entity.health_points <= 0 and entity.type != 'player':
            entities.pop(entities.index(entity))
            if random.random() > 0.30:
                items.append(Potion(50, 'healing_potion',
                                    entity.hitbox.center, 32, 32))

    if current_time % 100 == 0:
        boss.shoot(player.rect.center, time_passed_seconds)

    if is_close(boss.hitbox, player.hitbox, 200) and current_time - whirlwind_activation_time > boss.cooldowns['whirlwind']:
        whirlwind_activation_time = pygame.time.get_ticks()
        boss.ready = False

    if pygame.event.get(attack_with_delay) and not boss.ready:
        boss.whirlwind(player)
        boss.ready = True

    items_collisions = check_collision(player.hitbox, items)
    for item in items_collisions:
        item.heal(player)
        items.pop(items.index(item))

    camera.scroll()
    canvas.blit(background, (int(0 - camera.offset.x +
                                 camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))

    for entity in entities:
        entity.draw(canvas, camera.offset.x, camera.offset.y, player)

    for item in items:
        item.draw(canvas, camera.offset.x, camera.offset.y)

    window.blit(canvas, (0, 0))
    pygame.display.update()
