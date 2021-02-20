# Setup python
import os
import sys
import pygame
from pygame.locals import *
from data import *
from data.gameobjects.vector2 import Vector2
from player import Player
from boss import Boss
from enemy import Enemy
from projectile import Projectile
from data.camera.camera import *

# globals
BLACK = 0, 0, 0
WHITE = 255, 255, 255
FPS = 20  # frame rate
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

# player
player = Player()
player_list = pygame.sprite.Group()
player_list.add(player)
# player.rect.x = (SCREEN_SIZE[0]/2 - player.playerImgWidth / 2)
# player.rect.y = (SCREEN_SIZE[1]/2 - player.playerImgHeight / 2)

# enemies
enemy = Enemy()
enemy_list = pygame.sprite.Group()
enemy_list.add(enemy)

# boss
boss = Boss()
boss_list = pygame.sprite.Group()
boss_list.add(boss)

# projectiles
projectiles = []

# variables
running = True

#camera & methods
camera = Camera(player)
follow = Follow(camera, player)
border = Border(camera, player)
auto = Auto(camera, player)
camera.setmethod(border)


# Game Loop
while running:
    canvas.blit(background, (0 - camera.offset.x +
                             camera.CONST[0], 0 - camera.offset.y + camera.CONST[1]))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()
    key_direction = Vector2(0, 0)
    # movement
    if pressed_keys[K_LEFT] or pressed_keys[K_a]:
        key_direction.x = -1
        player.left = True
        player.right = False
    elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
        key_direction.x = +1
        player.right = True
        player.left = False
    if pressed_keys[K_UP] or pressed_keys[K_w]:
        key_direction.y = -1
    elif pressed_keys[K_DOWN] or pressed_keys[K_s]:
        key_direction.y = +1

    if pressed_keys[K_SPACE] and len(projectiles) == 0:
        if player.right:
            direction = 1
        else:
            direction = -1
        projectile = Projectile(
            Vector2(player.position.x - camera.offset.x, player.position.y - camera.offset.y), direction)
        projectiles.append(projectile)
    enemy_direction = Vector2(0, 0)
    enemy_direction.normalise()
    key_direction.normalize()

    time_passed = clock.tick(60)
    time_passed_seconds = time_passed / 1000.0
    random_rect = pygame.Rect(200 - camera.offset.x,
                              200 - camera.offset.y, 40, 80)
    enemy.update(enemy_direction, time_passed_seconds,
                 camera.offset.x, camera.offset.y)
    boss.update(enemy_direction, time_passed_seconds,
                camera.offset.x, camera.offset.y)

    player.update(key_direction, time_passed_seconds,
                  camera.offset.x, camera.offset.y)
    if projectiles:
        for projectile in projectiles:
            if projectile.rect.x > 1500 or projectile.rect.x < -380:
                projectiles.pop(projectiles.index(projectile))
            else:
                projectile.update(camera.offset.x, camera.offset.y)
                print("tu som ")

    # print(camera.offset)
    camera.scroll()
    if projectiles:
        for projectile in projectiles:
            projectile.draw(canvas)
    player.draw(canvas,
                camera.offset.x, camera.offset.y)

    if player.hitbox.colliderect(enemy.rect):
        print("hit")
    else:
        print("not hit")

    boss.draw(canvas, camera.offset.x, camera.offset.y)
    enemy.draw(canvas, camera.offset.x, camera.offset.y)
    pygame.draw.rect(canvas, (255, 0, 0), random_rect)

    window.blit(canvas, (0, 0))
    pygame.display.update()
