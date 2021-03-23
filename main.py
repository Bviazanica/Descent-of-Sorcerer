# Setup python
import os
import sys
import pygame
import random
from data import *
from utility import *
from boss import Boss
from enemy import Enemy
from pygame import mixer
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
pygame.mixer.pre_init(44100, 16, 2, 4096)
mixer.init()
pygame.init()
# sounds
main_background = pygame.mixer.music.load('data/sounds/main_background.wav')
# menu = pygame.mixer.music.load('data/sounds/menu.wav')
# death_screen = pygame.mixer.music.load('data/sounds/death_screen.wav')

# Titles
pygame.display.set_caption("Game")

# background
background = pygame.image.load(
    'data/images/backgrounds/background.png').convert()
front_decor = pygame.image.load(
    'data/images/backgrounds/front_decor.png').convert()
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
pygame.mixer.music.play(-1, 0.0)
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

        if pressed_keys[K_SPACE] and current_time - player.range_attack_time > player.cooldowns['range']:
            if player.state == 'RUNNING':
                player.state = player.states['RUNNING-FIRING']
            else:
                player.state = player.states['FIRING']

        if pressed_keys[K_f] and current_time - player.melee_attack_time > player.cooldowns['melee']:

            if player.state == 'RUNNING':
                player.state = player.states['RUNNING-ATTACKING']
            else:
                player.state = player.states['ATTACKING']

        if not pressed_keys.count(1) and player.state != player.states['HURTING'] and player.state != player.states['DYING'] and player.init_state:
            player.state = player.states['IDLING']

        movement.normalize()
    for entity in entities:
        if entity.type == 'player':
            entity.update(time_passed_seconds, movement,
                          entities)
        elif entity.type == 'boss':
            entity.update(player, time_passed_seconds, movement,
                          entities, Enemy)
            if entity.entities_summoned:
                entities.extend(entity.get_summoned_entities())
                entity.entities_summoned = False
        elif entity.type == 'mob':
            entity.update(time_passed_seconds, player,
                          get_entities(entities, 'mob'))

        if not entity.is_alive and entity.type != 'player' and entity.init_state:
            if random.random() > 0.75:
                items.append(Potion(50, 'potion',
                                    entity.hitbox.center, 32, 32))
            entities.pop(entities.index(entity))

    items_collisions = check_collision(player.hitbox, items)
    for item in items_collisions:
        item.heal(player, items)
    # print(
    #     f'{player.action} & {player.state} & {player.init_state} & {player.frame_index} {current_time - melee_attack_time > player.cooldowns["melee"]}')
    camera.scroll()
    canvas.blit(background, (int(0 - camera.offset.x +
                                 camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))

    for item in items:
        item.draw(canvas, camera.offset.x, camera.offset.y)
    for entity in entities:
        entity.draw(canvas, camera.offset.x, camera.offset.y, player)

    canvas.blit(front_decor, (int(0 - camera.offset.x +
                                  camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
    window.blit(canvas, (0, 0))
    pygame.display.update()
