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
tutorial_text = pygame.Surface((window.get_width(), 100)).convert_alpha()
tutorial_text.fill((0, 0, 0, 180))

# death screen menu
restart_button = Button(SCREEN_SIZE[0]//2, 300, 'menu')
menu_button = Button(SCREEN_SIZE[0]//2, 400, 'menu')
# menu
game_button = Button(SCREEN_SIZE[0]//2, 100, 'menu')
controls_button = Button(SCREEN_SIZE[0]//2, 200, 'menu')
credits_button = Button(SCREEN_SIZE[0]//2, 300, 'menu')
quit_button = Button(SCREEN_SIZE[0]//2, 400, 'menu')
# tutorial
next_button = Button(SCREEN_SIZE[0] - 25, SCREEN_SIZE[1] - 25, 'arrow')

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
stages = {'tutorial': 'tutorial', 'starting': 'starting',
          'fighting': 'fighting', 'ending': 'ending'}
tutorial_stages = ['movement', 'attacks', 'game', 'pause']

tutorial = True
paused = False

stage_loading_time = 5000
wave_number = 0
pygame.mixer.music.set_volume(0.1)


def game():

    load_music('main_background')
    pygame.mixer.music.play(-1, 0.0)

    entities.clear()
    items.clear()
    mobs.clear()
    player = Player(400, 200)
    entities.append(player)
    # boss = Boss()
    # entities.append(boss)
    death_screen_running = False
    camera = Camera(player)
    border = Border(camera, player)
    camera.setmethod(border)
    running = True
    current_time = 0
    time_before_pause = 0
    enemies_to_defeat = 6
    boss_fight = False
    if tutorial:
        stage = stages['tutorial']
        tutorial_stage_index = 0
        new_tutorial_stage = True
        tutorial_stage = tutorial_stages[tutorial_stage_index]
    else:
        stage = stages['starting']
        stage_start = 0
        new_stage = True
    # Game Loop
    while running:
        # frame interval
        global wave_number
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
                    pygame.mixer.music.unload()
                if event.key == K_p:
                    paused = not paused
                    if paused:
                        time_before_pause = current_time
                    if not paused:
                        current_time = time_before_pause
        pressed_keys = pygame.key.get_pressed()
        movement = Vector2(0, 0)
        if not paused:
            if not player.is_alive:
                if player.death_screen_ready:
                    death_screen_running = True
                    pygame.mixer.music.load(
                        f'data/sounds/death_screen.wav')
                    pygame.mixer.music.play(-1, 0.0)
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

                            player = Player(400, 200)
                            entities.append(player)

                            camera = Camera(player)
                            border = Border(camera, player)
                            camera.setmethod(border)

                            current_time = 0
                            time_before_pause = 0
                            player.death_screen_ready = False
                            death_screen_running = False
                            stage = stages['starting']
                            stage_start = 0

                        if menu_button.draw(canvas):
                            running = False
                            player.death_screen_ready = False
                            death_screen_running = False
                            pygame.mixer.music.unload()

                        draw_text('GAME OVER', font_arial_big, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 200-15)
                        draw_text('Restart', font_arial, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 300-15)
                        draw_text('Back to menu', font_arial, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 400-15)
                        window.blit(canvas, (0, 0))
                        pygame.display.update()
            else:
                if stage == stages['starting']:
                    if new_stage:
                        if not boss_fight:
                            wave_number += 1

                        stage_start = current_time
                        new_stage = False
                    if wave_number % 1 == 0:
                        boss_fight = True
                    if current_time - stage_start > stage_loading_time:
                        stage = stages['fighting']
                        new_stage = True
                        mobs.clear()
                        enemies_to_defeat = 6
                elif stage == stages['fighting']:
                    if boss_fight:
                        if new_stage:
                            boss = Boss(920, 100)
                            boss.desired_appear = Vector2(
                                220, boss.rect.y)
                            entities.append(boss)
                            new_stage = False
                    elif new_stage:
                        # spawn mobs
                        mobs.extend(
                            summon(Enemy, random.choice(
                                [-420, 930]), 50, 2, wave_number, 150))
                        new_stage = False
                        entities.extend(mobs)
                    elif not boss_fight:
                        if len(mobs) < 1 and enemies_to_defeat > 0:
                            mobs.extend(
                                summon(Enemy, 920, 50, 2, wave_number, 150))
                            entities.extend(mobs)
                        elif len(mobs) < 1 and enemies_to_defeat < 1:
                            stage = stages['ending']
                            new_stage = True
                elif stage == stages['ending']:
                    if new_stage:
                        stage_start = current_time
                        wave_complete_sound.play()
                        new_stage = False
                    if current_time - stage_start > stage_loading_time:
                        stage = stages['starting']
                        new_stage = True
                    # upgrade wave

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
                                  entities, stage)
                elif entity.type == 'boss':
                    entity.update(player, current_time, time_passed_seconds, movement,
                                  entities, Enemy, stage, wave_number)
                    if entity.entities_summoned:
                        boss_summons = entity.get_summoned_entities()
                        mobs.extend(boss_summons)
                        entities.extend(mobs)
                        entity.entities_summoned = False
                elif entity.type == 'mob':
                    entity.update(current_time, time_passed_seconds, player,
                                  get_entities(entities, 'mob'), stage)

                if not entity.is_alive and entity.init_state and entity.type != 'player':
                    if entity.type == 'mob':
                        if random.random() > 0.75:
                            items.append(Potion(50, 'potion',
                                                entity.hitbox.center, 32, 32))
                        mobs.pop(mobs.index(entity))
                        enemies_to_defeat -= 1
                    if entity.type == 'boss':
                        stage = stages['ending']
                        new_stage = True

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

        canvas.blit(front_decor, (int(0 - camera.offset.x +
                                      camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
        if stage == stages['tutorial']:
            canvas.blit(tutorial_text, (0, SCREEN_SIZE[1] - 100))

            if next_button.draw(canvas):
                if tutorial_stage_index == len(tutorial_stages)-1:
                    stage = stages['starting']
                    new_stage = True
                else:
                    tutorial_stage_index += 1
                    tutorial_stage = tutorial_stages[tutorial_stage_index]
                    new_tutorial_stage = True
                    tutorial_text.fill((0, 0, 0, 180))

            if new_tutorial_stage:
                new_tutorial_stage = False
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.movement)]:
                    draw_text('Move with W,A,S,D or with arrow keys on your keyboard.', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.attacks)]:

                    draw_text('You have two abilities, melee and fireball.', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                    draw_text('Each ability has a cooldown time.', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 35)
                    draw_text('Melee attacks can hit multiple enemies.', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 60)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.game)]:
                    draw_text('Fight your way through waves of enemies to challange the boss.', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.pause)]:
                    draw_text('You can pause your game anytime by pressing P', font_arial, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)

        elif stage == stages['starting']:
            draw_text('Wave '+str(wave_number), humongous_font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)
        elif stage == stages['fighting']:
            draw_text('Wave '+str(wave_number), font_arial_bold, WHITE,
                      canvas, SCREEN_SIZE[0] - 50, 5)
        elif stage == stages['ending']:
            draw_text('Wave '+str(wave_number) + ' completed', humongous_font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)

        if paused:
            canvas.blit(dim_screen, (0, 0))
            draw_text('PAUSED', humongous_font_arial, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)

        window.blit(canvas, (0, 0))
        pygame.display.update()


def main_menu():
    pygame.mixer.music.load(f'data/sounds/menu.wav')
    pygame.mixer.music.play(-1, 0.0)
    clicked = False
    while True:
        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0
        canvas.fill((0, 0, 0))

        mx, my = pygame.mouse.get_pos()

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


def start_wave():
    draw_text('Wave ' + str(wave_number), humongous_font_arial,
              WHITE, canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)


main_menu()
