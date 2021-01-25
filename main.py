# Setup python
import os
import sys
import pygame
from pygame.locals import *
from data import *
from data.gameobjects.vector2 import Vector2
from player import Player

# globals
SCREEN_SIZE = width, height = 800, 600
BLACK = 0, 0, 0
WHITE = 255, 255, 255
FPS = 20  # frame rate
screen = pygame.display.set_mode(SCREEN_SIZE)
display = pygame.Surface((640, 480))
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
player.rect.x = (SCREEN_SIZE[0]/2 - player.playerImgWidth / 2)
player.rect.y = (SCREEN_SIZE[1]/2 - player.playerImgHeight / 2)
player_list = pygame.sprite.Group()
player_list.add(player)


# variables
scroll = [0, 0]
true_scroll = [(SCREEN_SIZE[0]/2 - player.playerImgWidth / 2),
               (SCREEN_SIZE[1]/2 - player.playerImgHeight / 2)]
running = True
# background
bgWidth = background.get_width()
bgHeight = background.get_height()


# Game Loop
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            running = False
    true_scroll[0] += (player.rect.x - true_scroll[0]-120)/10
    print("TS 0 " + str(true_scroll[0]))
    true_scroll[1] += (player.rect.y - true_scroll[1]-68)/10
    scroll = [int(true_scroll[0]), int(true_scroll[1])]
    display.fill(BLACK)
    if scroll[1] > 200:
        scroll[1] = 200
    if scroll[1] < -200:
        scroll[1] = -200
    if scroll[0] < -200:
        scroll[0] = -200
    if scroll[0] > 200:  # ked je x hraca vacsie ako 67 tak sa posunie normalne
        scroll[0] = 200
    display.blit(background, (-scroll[0] - 200, -scroll[1]-200))
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
    player.update(key_direction, time_passed_seconds)
    screen.blit(pygame.transform.scale(display, (SCREEN_SIZE)), (0, 0))
    player_list.draw(screen)
    pygame.display.update()
