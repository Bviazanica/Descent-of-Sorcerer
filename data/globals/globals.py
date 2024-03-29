import pygame
from enum import IntEnum

pygame.init()

# font
humongous_font_gothikka = pygame.font.Font('data/fonts/Gothikka Bold.ttf', 70)
humongous_font_gothikka.set_bold(True)
font_gothikka = pygame.font.Font('data/fonts/Gothikka.ttf', 24)
font_gothikka.set_bold(True)
font_gothikka_big = pygame.font.Font('data/fonts/Gothikka Bold.ttf', 54)
font_gothikka_smaller = pygame.font.Font('data/fonts/Gothikka.ttf', 24)
font_gothikka_bold = pygame.font.Font('data/fonts/Gothikka Bold.ttf', 30)
font_gothikka_bold.set_bold(True)
font_gothikka_bold_numbers = pygame.font.Font(
    'data/fonts/Gothikka Bold.ttf', 28)
font_gothikka_bold_numbers.set_bold(True)

boss_hurt_sound = pygame.mixer.Sound('data/sounds/boss_hurt.wav')
fireball_hit_sound = pygame.mixer.Sound('data/sounds/fireball_hit.wav')
fireball_cast_sound = pygame.mixer.Sound('data/sounds/fireball_cast.wav')
fireball_cast2_sound = pygame.mixer.Sound('data/sounds/fireball_cast2.wav')
hit_sound = pygame.mixer.Sound('data/sounds/hit.wav')
menu_select_sound = pygame.mixer.Sound('data/sounds/menu_select.wav')
mob_death_sound = pygame.mixer.Sound('data/sounds/mob_death.wav')
potion_sound = pygame.mixer.Sound('data/sounds/potion.wav')
next_click_sound = pygame.mixer.Sound('data/sounds/next_click.wav')
swing_sound = pygame.mixer.Sound('data/sounds/swing.wav')
throw_sound = pygame.mixer.Sound('data/sounds/throw.wav')
bonk_sound = pygame.mixer.Sound('data/sounds/bonk.wav')
decoy_sound = pygame.mixer.Sound('data/sounds/decoy.wav')
wave_complete_sound = pygame.mixer.Sound('data/sounds/wave_complete.wav')
lightning_sound = pygame.mixer.Sound('data/sounds/lightning.wav')
explode_sound = pygame.mixer.Sound('data/sounds/explode.wav')
win_sound = pygame.mixer.Sound('data/sounds/win.wav')
upgrade_abilities_sound = pygame.mixer.Sound(
    'data/sounds/upgrade_abilities.wav')
upgrade_sound = pygame.mixer.Sound('data/sounds/upgrade.wav')
ability_learn_sound = pygame.mixer.Sound('data/sounds/ability_learn.wav')

sound_effects = []
sound_effects.extend([
                      boss_hurt_sound,
                      fireball_hit_sound,
                      fireball_cast_sound,
                      fireball_cast2_sound,
                      hit_sound,
                      menu_select_sound,
                      mob_death_sound,
                      potion_sound,
                      swing_sound,
                      throw_sound,
                      bonk_sound,
                      wave_complete_sound,
                      ability_learn_sound,
                      upgrade_abilities_sound,
                      upgrade_sound,
                      win_sound,
                      explode_sound,
                      lightning_sound,
                      decoy_sound,
                      next_click_sound
                      ])

FPS = 60  # frame rate
SCREEN_SIZE = width, height = 800, 600
# colors
BLACK = 0, 0, 0
WHITE = (255, 255, 255)
RED = (240, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 191, 255)
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
    Summoning = 13,
    Falling = 14,
    Exploding = 15,


class Tutorial_stage(IntEnum):
    movement = 0,
    attacks = 1,
    game = 2,
    pause = 3
