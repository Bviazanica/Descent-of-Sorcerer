# Setup python
import os
import sys
import pygame
from pygame.locals import *
from data import *
from data.gameobjects.vector2 import Vector2

# variables
SCREEN_SIZE = width, height = 640, 480
BLACK = 0, 0, 0
WHITE = 255, 255, 255
FPS = 30  # frame rate

# setup
clock = pygame.time.Clock()
pygame.init()

# create the canvas
screen = pygame.display.set_mode(SCREEN_SIZE)
running = True

# Title
pygame.display.set_caption("Celestial")

# images
# background = pygame.image.load('data/images/backgrounds/bg_1.png').convert()
playerImg = pygame.image.load('data/images/entities/hero/hero.png').convert()
playerImg = pygame.transform.scale(playerImg, (36, 64))

# player
playerImgWidth = playerImg.get_width()
playerImgHeight = playerImg.get_height()
# starting position
playerX = (width / 2) - (playerImgWidth / 2)
playerY = height - playerImgHeight
speed_x, speed_y = 0, 150

# functions
player_pos = Vector2(playerX, playerY)
player_speed = 300


def player(pos):
    screen.blit(playerImg, pos)


# Game Loop
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            running = False

    pressed_keys = pygame.key.get_pressed()

    key_direction = Vector2(0, 0)

    if pressed_keys[K_LEFT]:
        key_direction.x = -1
    elif pressed_keys[K_RIGHT]:
        key_direction.x = +1
    if pressed_keys[K_UP]:
        key_direction.y = -1
    elif pressed_keys[K_DOWN]:
        key_direction.y = +1

    key_direction.normalize()

    time_passed = clock.tick(FPS)
    time_passed_seconds = time_passed / 1000.0
    player_pos += key_direction * player_speed * time_passed_seconds
    player(player_pos)
    pygame.display.flip()
