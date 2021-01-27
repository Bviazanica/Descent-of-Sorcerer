# Setup python
import os
import sys
import pygame
from pygame.locals import *
from data import *
from data.gameobjects.vector2 import Vector2
from player import Player
from data.camera.camera import *

# globals
SCREEN_SIZE = width, height = 800, 600
BLACK = 0, 0, 0
WHITE = 255, 255, 255
FPS = 20  # frame rate
window = pygame.display.set_mode(SCREEN_SIZE)
canvas = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))
# setup
clock = pygame.time.Clock()
pygame.init()

# Title
pygame.display.set_caption("Celestial")

# images
background = pygame.image.load(
    'data/images/backgrounds/bg_1.png').convert()

# player
player = Player()
# player.rect.x = (SCREEN_SIZE[0]/2 - player.playerImgWidth / 2)
# player.rect.y = (SCREEN_SIZE[1]/2 - player.playerImgHeight / 2)
player_list = pygame.sprite.Group()
player_list.add(player)


# variables

running = True
# background
bgWidth = background.get_width()
bgHeight = background.get_height()

camera = Camera(player)
follow = Follow(camera, player)
border = Border(camera, player)
auto = Auto(camera, player)
camera.setmethod(auto)

# Game Loop
while running:
    canvas.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            running = False

    pressed_keys = pygame.key.get_pressed()
    key_direction = Vector2(0, 0)
    if pressed_keys[K_LEFT] or pressed_keys[K_a]:
        key_direction.x = -1
    elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
        key_direction.x = +1
    if pressed_keys[K_UP] or pressed_keys[K_w]:
        key_direction.y = -1
    elif pressed_keys[K_DOWN] or pressed_keys[K_s]:
        key_direction.y = +1
    key_direction.normalize()
    time_passed = clock.tick(FPS)
    time_passed_seconds = time_passed / 1000.0
    canvas.blit(background, (0 - camera.offset.x +
                             camera.CONST[0], 0 - camera.offset.y + camera.CONST[1]))
    player.update(key_direction, time_passed_seconds)
    player.draw(canvas, camera.offset.x, camera.offset.y)
    camera.scroll()
    print(player.player_pos)
    window.blit(canvas, (0, 0))
    pygame.display.update()
