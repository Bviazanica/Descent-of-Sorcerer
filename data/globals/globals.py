import pygame
from enum import IntEnum
from pygame import mixer

pygame.mixer.pre_init(44100, 16, 2, 4096)
mixer.init()

boss_battle_sound = pygame.mixer.Sound('data/sounds/boss_battle.wav')
boss_hurt_sound = pygame.mixer.Sound('data/sounds/boss_hurt.wav')
fireball_hit_sound = pygame.mixer.Sound('data/sounds/fireball_hit.wav')
fireball_cast_sound = pygame.mixer.Sound('data/sounds/fireball_cast.wav')
fireball_cast2_sound = pygame.mixer.Sound('data/sounds/fireball_cast2.wav')
hit_sound = pygame.mixer.Sound('data/sounds/hit.wav')
menu_select_sound = pygame.mixer.Sound('data/sounds/menu_select.wav')
mob_death_sound = pygame.mixer.Sound('data/sounds/mob_death.wav')
potion_sound = pygame.mixer.Sound('data/sounds/potion.wav')
swing_sound = pygame.mixer.Sound('data/sounds/swing.wav')
throw_sound = pygame.mixer.Sound('data/sounds/throw.wav')
bonk_sound = pygame.mixer.Sound('data/sounds/bonk.wav')
wave_complete_sound = pygame.mixer.Sound('data/sounds/wave_complete.wav')

FPS = 60  # frame rate
SCREEN_SIZE = width, height = 800, 600
# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (240, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)


CAMERA_TOP, CAMERA_BOTTOM = -260, 460
CAMERA_LEFT, CAMERA_RIGHT = -365, 915

LEFT_BORDER, RIGHT_BORDER = -365, 915
TOP_BORDER, BOTTOM_BORDER = 20, 460


class Animation_type(IntEnum):
    Dying = 0,
    Hurt = 1,
    Idle = 2,
    Idle_Blinking = 3,
    Kicking = 4,
    Run_Slashing = 5,
    Run_Throwing = 6,
    Running = 7,
    Slashing = 8,
    Slashing_in_The_Air = 9,
    Throwing = 10,
    Throwing_in_The_Air = 11,
    Walking = 12,
    Summoning = 13
