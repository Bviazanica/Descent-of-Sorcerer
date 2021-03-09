# Setup python
import os
import sys
import pygame
import pygame_ai as pai
from pygame.locals import *
from data import *
from data.gameobjects.vector2 import Vector2
from player import Player
from boss import Boss
from circle import CircleNPC
from enemy import Enemy
from data.camera.camera import *

# globals
BLACK = 0, 0, 0
WHITE = 255, 255, 255
FPS = 60  # frame rate
SCREEN_SIZE = width, height = 800, 600


# window & canvas
window = pygame.display.set_mode(SCREEN_SIZE)
canvas = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))

# setup
clock = pygame.time.Clock()
pygame.init()

# Title
pygame.display.set_caption("Celestial")

# background
background = pygame.image.load(
    'data/images/backgrounds/bg_1.png').convert()
bgWidth = background.get_width()
bgHeight = background.get_height()

# entities
player = Player()
enemy = Enemy()
boss = Boss()


# camera & methods
camera = Camera(player)
follow = Follow(camera, player)
border = Border(camera, player)
auto = Auto(camera, player)
camera.setmethod(border)

# variables
collision_objects = []
projectile_collision = []
running = True
current_time = 0
collision_objects.extend([enemy, boss])

# player cooldowns
melee_attack_time = 0
range_attack_time = 0

circle = CircleNPC(pos=(100, 100))
circle.ai = pai.steering.kinematic.Wander(
    circle, 50, 15, 20)
drag = pai.steering.kinematic.Drag(15)


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
    # movement
    if pressed_keys[K_LEFT] or pressed_keys[K_a]:
        movement.x = -1
        player.left = True
        player.right = False
    elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
        movement.x = +1
        player.right = True
        player.left = False
    if pressed_keys[K_UP] or pressed_keys[K_w]:
        movement.y = -1
    elif pressed_keys[K_DOWN] or pressed_keys[K_s]:
        movement.y = +1

    if pressed_keys[K_SPACE] and current_time - range_attack_time > player.cooldowns['range']:
        range_attack_time = pygame.time.get_ticks()
        player.fire(canvas, collision_objects,
                    camera.offset.x, camera.offset.y)

    if pressed_keys[K_f] and current_time - melee_attack_time > player.cooldowns['melee']:
        melee_attack_time = pygame.time.get_ticks()
        player.melee_attack(canvas, collision_objects,
                            camera.offset.x, camera.offset.y)

    enemy_direction = Vector2(0, 0)
    enemy_direction.normalise()
    movement.normalize()

    player.update(canvas, time_passed_seconds, movement,
                  collision_objects, camera.offset.x, camera.offset.y)
    enemy.update()
    boss.update()
    circle.update(time_passed_seconds)
    canvas.blit(background, (int(0 - camera.offset.x +
                                 camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
    circle.steer(drag.get_steering(circle), time_passed_seconds)
    camera.scroll()
    player.draw(canvas, camera.offset.x, camera.offset.y)
    boss.draw(canvas, camera.offset.x, camera.offset.y)
    enemy.draw(canvas, camera.offset.x, camera.offset.y)
    canvas.blit(circle.image, (int(circle.rect.x - camera.offset.x),
                               int(circle.rect.y - camera.offset.y)))

    window.blit(canvas, (0, 0))
    pygame.display.update()
