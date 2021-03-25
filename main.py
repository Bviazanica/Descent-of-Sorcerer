# Setup python
import os
import sys
import pygame
import random
from data import *
from utility import *
from boss import Boss
from button import Button
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
# dim screen
dim_screen = pygame.Surface(window.get_size()).convert_alpha()
dim_screen.fill((0, 0, 0, 180))
# music
pygame.mixer.music.play(-1, 0.0)
# death screen menu
restart_button = Button(SCREEN_SIZE[0]//2, 300)
menu_button = Button(SCREEN_SIZE[0]//2, 400)
# menu
game_button = Button(SCREEN_SIZE[0]//2, 100)
continue_button = Button(SCREEN_SIZE[0]//2, 100)
controls_button = Button(SCREEN_SIZE[0]//2, 200)
credits_button = Button(SCREEN_SIZE[0]//2, 300)
quit_button = Button(SCREEN_SIZE[0]//2, 400)

# font
font_name = pygame.font.match_font('arial')
humongous_font_arial = pygame.font.SysFont(font_name, 64, True, False)
font_arial = pygame.font.Font(font_name, 24)
font_arial_big = pygame.font.Font(font_name, 32)
font_arial_smaller = pygame.font.Font(font_name, 14)
font_arial_bold = pygame.font.SysFont(font_name, 24, True, False)
entities = []
items = []
mobs = []


paused = False


def game():
    entities.clear()
    items.clear()
    mobs.clear()
    player = Player(-200, 100)
    entities.append(player)
    boss = Boss()
    entities.append(boss)
    death_screen_running = False
    camera = Camera(player)
    border = Border(camera, player)
    camera.setmethod(border)
    current_time = 0
    wave_number = 1
    running = True
    current_time = 0
    time_before_pause = 0
    # Game Loop
    while running:
        # frame interval
        global paused
        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0
        canvas.fill(BLACK)
        current_time += time_passed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and player.is_alive:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_p:
                    paused = not paused
                    if paused:
                        time_before_pause = current_time
                    if not paused:
                        current_time = time_before_pause
        pressed_keys = pygame.key.get_pressed()
        movement = Vector2(0, 0)
        # print(f'CT{current_time} & PT{time_before_pause}')

        if not paused:
            if not player.is_alive:
                if player.death_screen_ready:
                    death_screen_running = True
                    while death_screen_running:
                        canvas.fill((0, 0, 0))
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                pygame.quit()
                                sys.exit()

                        if restart_button.draw(canvas):
                            entities.clear()
                            items.clear()
                            mobs.clear()

                            player = Player(-200, 100)
                            entities.append(player)

                            boss = Boss()
                            entities.append(boss)

                            camera = Camera(player)
                            border = Border(camera, player)
                            camera.setmethod(border)

                            current_time = 0
                            player.death_screen_ready = False
                            death_screen_running = False
                        if menu_button.draw(canvas):
                            player.death_screen_ready = False
                            death_screen_running = False
                            running = False
                        draw_text('GAME OVER', font_arial_big, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 200-15)
                        draw_text('Restart', font_arial, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 300-15)
                        draw_text('Back to menu', font_arial, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 400-15)
                        window.blit(canvas, (0, 0))
                        pygame.display.update()
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
                    entity.update(current_time, time_passed_seconds, movement,
                                  entities)
                elif entity.type == 'boss':
                    entity.update(player, current_time, time_passed_seconds, movement,
                                  entities, Enemy)
                    if entity.entities_summoned:
                        entities.extend(entity.get_summoned_entities())
                        entity.entities_summoned = False
                elif entity.type == 'mob':
                    entity.update(current_time, time_passed_seconds, player,
                                  get_entities(entities, 'mob'))

                if not entity.is_alive and entity.type != 'player' and entity.init_state:
                    if random.random() > 0.75:
                        items.append(Potion(50, 'potion',
                                            entity.hitbox.center, 32, 32))
                    entities.pop(entities.index(entity))

            items_collisions = check_collision(player.hitbox, items)
            for item in items_collisions:
                item.heal(player, items)
            camera.scroll()
        canvas.blit(background, (int(0 - camera.offset.x +
                                     camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))

        for item in items:
            item.draw(canvas, camera.offset.x, camera.offset.y)
        for entity in entities:
            entity.draw(canvas, camera.offset.x, camera.offset.y, player)

        draw_text('Wave '+str(wave_number), font_arial_bold, WHITE,
                  canvas, SCREEN_SIZE[0] - 50, 5)
        canvas.blit(front_decor, (int(0 - camera.offset.x +
                                      camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))

        if paused:
            canvas.blit(dim_screen, (0, 0))
            draw_text('PAUSED', humongous_font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)
        window.blit(canvas, (0, 0))
        pygame.display.update()


def main_menu():
    clicked = False
    while True:
        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0
        canvas.fill((0, 0, 0))

        mx, my = pygame.mouse.get_pos()

        if paused:
            if continue_button.draw(canvas):
                if clicked:
                    game()
        else:
            if game_button.draw(canvas):
                if clicked:
                    game()
        if controls_button.draw(canvas):
            if clicked:
                controls()
        if credits_button.draw(canvas):
            if clicked:
                show_credits()
        if quit_button.draw(canvas):
            if clicked:
                pygame.quit()
                sys.exit()

        clicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
        if paused:
            draw_text('Continue', font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]//2, 100-15)
        else:
            draw_text('Start new game', font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]//2, 100-15)
        draw_text('Controls', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 200-15)
        draw_text('Credits', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 300-15)
        draw_text('Quit', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 400-15)
        window.blit(canvas, (0, 0))
        pygame.display.update()


def controls():
    running = True
    while running:
        canvas.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        draw_text('Move up', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 100-10)
        draw_text('W or Arrow up', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 100)
        draw_text('Move down', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 150-10)
        draw_text('S or Arrow down', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 150)
        draw_text('Move left', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 200-10)
        draw_text('A or Arrow left', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 200)
        draw_text('Move right', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 250-10)
        draw_text('D or Arrow right', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 250)
        draw_text('Cast fireball', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 300-10)
        draw_text('SPACE', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 300)
        draw_text('Melee attack', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 350-10)
        draw_text('F', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 350)
        draw_text('Return to menu', font_arial, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 400-10)
        draw_text('Escape', font_arial_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 400)
        window.blit(canvas, (0, 0))
        pygame.display.update()


def show_credits():
    running = True
    while running:
        canvas.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        draw_text('Credits', font_arial_big, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 100-10)

        window.blit(canvas, (0, 0))
        pygame.display.update()


main_menu()
