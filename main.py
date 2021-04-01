# Setup python
import os
import sys
import pygame
import random
from data.utility import *
from data.boss import Boss
from data.button import Button
from data.enemy import Enemy
from pygame import mixer
from data.player import Player
from pygame.locals import *
from data.camera.camera import *
from data.globals.globals import *
from data.toggle_music import Pause
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
entities = []
items = []
mobs = []
stages = {'tutorial': 'tutorial', 'starting': 'starting',
          'fighting': 'fighting', 'ending': 'ending'}
tutorial_stages = ['movement', 'attacks', 'game', 'pause']

tutorial = True
paused = False
clickable = True
stage_loading_time = 200
wave_number = 0
boss_fight = False
pygame.mixer.music.set_volume(0.1)
music_handler = Pause()
music_handler.set_all_sounds_volume(0.5)
spawn_cooldown = 15000


def game():
    load_music('main_background')
    if not music_handler.paused:
        pygame.mixer.music.play(-1, 0.0)
    global wave_number
    entities.clear()
    items.clear()
    mobs.clear()
    player = Player(400, 200)
    entities.append(player)
    death_screen_running = False
    camera = Camera(player)
    border = Border(camera, player)
    camera.setmethod(border)
    running = True
    current_time = 0
    time_before_pause = 0
    enemies_to_defeat = 0
    wave_number = 0
    spawn_mobs_number = 4
    total_mobs_per_wave = 2
    max_spawn_mobs_number = 8
    last_spawned_time = 0
    start_upgrade_after_wave = 5
    remaining_mobs = 0
    boss = []
    # tutorial
    next_button = Button(
        SCREEN_SIZE[0] - 25, SCREEN_SIZE[1] - 25, 'arrow')
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
        pygame.mixer.music.set_volume(0.1)
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
                    load_music('menu')
                    if not music_handler.paused:
                        pygame.mixer.music.play(-1, 0.0)
                if event.key == K_p:
                    paused = not paused
                    if paused:
                        time_before_pause = current_time
                    if not paused:
                        current_time = time_before_pause
                if event.key == K_m:
                    music_handler.toggle()

        pressed_keys = pygame.key.get_pressed()
        movement = Vector2(0, 0)
        if not paused:
            if not player.is_alive:
                if player.death_screen_ready:
                    # death screen menu
                    restart_button = Button(SCREEN_SIZE[0]//2, 300, 'menu')
                    menu_button = Button(SCREEN_SIZE[0]//2, 400, 'menu')
                    death_screen_running = True
                    load_music('death_screen')
                    if not music_handler.paused:
                        pygame.mixer.music.play(-1, 0.0)
                    while death_screen_running:
                        clickable = True
                        canvas.fill((0, 0, 0))
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == KEYDOWN:
                                if event.key == K_m:
                                    music_handler.toggle()

                        if restart_button.draw(canvas):
                            if clickable:
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
                                wave_number = 1
                                enemies_to_defeat = 2
                                spawn_mobs_number = 4
                                load_music('main_background')
                                if not music_handler.paused:
                                    pygame.mixer.music.play(-1, 0.0)
                                clickable = False

                        if menu_button.draw(canvas):
                            if clickable:
                                player.death_screen_ready = False
                                death_screen_running = False
                                running = False
                                load_music('menu')
                                if not music_handler.paused:
                                    pygame.mixer.music.play(-1, 0.0)
                                clickable = False

                        draw_text('GAME OVER', font_gothikka_big, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 200)
                        draw_text('Restart', font_gothikka, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 300+12)
                        draw_text('Back to menu', font_gothikka, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 400+12)
                        window.blit(canvas, (0, 0))
                        pygame.display.update()

            else:
                if stage == stages['starting']:
                    if new_stage:
                        wave_number += 1
                        boss_fight = False
                        if wave_number % 1 == 0:
                            boss_fight = True
                        else:
                            total_mobs_per_wave += 2
                            enemies_to_defeat = total_mobs_per_wave
                        stage_start = current_time
                        new_stage = False
                    if current_time - stage_start > stage_loading_time:
                        stage = stages['fighting']
                        new_stage = True

                elif stage == stages['fighting']:
                    if boss_fight:
                        if new_stage:
                            boss = Boss(400, -420)
                            boss.desired_appear = Vector2(
                                boss.rect.centerx, 100)
                            upgrade_boss(boss, wave_number)
                            entities.append(boss)
                            new_stage = False
                            if spawn_mobs_number < max_spawn_mobs_number:
                                spawn_mobs_number += 4
                        if len(mobs) < 1 and not boss.is_alive:
                            stage = stages['ending']
                            new_stage = True
                            boss_fight = False
                    elif new_stage:
                        last_spawned_time = current_time
                        spawn_coords_x = random.choice([-450, 930])
                        desired_coords_offset = 100
                        if spawn_coords_x > 0:
                            desired_coords_offset *= -1
                        new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number,
                                          wave_number, desired_coords_offset, True, start_upgrade_after_wave)
                        new_stage = False
                        mobs.extend(new_mobs)
                        entities.extend(new_mobs)
                    elif not boss_fight:
                        spawn_coords_x = random.choice([-450, 930])
                        desired_coords_offset = 100
                        if spawn_coords_x > 0:
                            desired_coords_offset *= -1
                        remaining_mobs = enemies_to_defeat - len(mobs)
                        if len(mobs) < 1 and enemies_to_defeat > 0:
                            if enemies_to_defeat >= spawn_mobs_number:
                                last_spawned_time = current_time
                                new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number//2,
                                                  wave_number, desired_coords_offset, True, start_upgrade_after_wave)
                            elif enemies_to_defeat >= spawn_mobs_number//2:
                                last_spawned_time = current_time
                                new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number//2,
                                                  wave_number, desired_coords_offset, True, start_upgrade_after_wave)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        elif remaining_mobs >= spawn_mobs_number and current_time - last_spawned_time > spawn_cooldown:
                            last_spawned_time = current_time
                            new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number,
                                              wave_number, desired_coords_offset, True, start_upgrade_after_wave)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        elif remaining_mobs < spawn_mobs_number and remaining_mobs > 0 and current_time - last_spawned_time > spawn_cooldown:
                            last_spawned_time = current_time
                            new_mobs = summon(Enemy, spawn_coords_x, 50, remaining_mobs,
                                              wave_number, desired_coords_offset, True, start_upgrade_after_wave)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        if enemies_to_defeat < 1 and len(mobs) < 1:
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
                                  entities, Enemy, stage, wave_number, start_upgrade_after_wave)
                    if entity.entities_summoned:
                        boss_summons = entity.get_summoned_entities()
                        enemies_to_defeat = len(boss_summons)
                        mobs.extend(boss_summons)
                        entities.extend(boss_summons)
                        entity.entities_summoned = False
                elif entity.type == 'mob':
                    entity.update(current_time, time_passed_seconds, player,
                                  get_entities_to_avoid(entities), stage, boss)

            for mob in mobs.copy():
                if not mob.is_alive and mob.init_state:
                    if random.random() > 0.85:
                        items.append(Potion(50, 'potion',
                                            entity.hitbox.center, 32, 32))
                    mobs.pop(mobs.index(mob))
            for entity in entities.copy():
                if not entity.is_alive and entity.init_state and entity.type != 'player':
                    if entity.type == 'mob':
                        enemies_to_defeat -= 1

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
                    draw_text('Move with W,A,S,D or with arrow keys on your keyboard.', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.attacks)]:

                    draw_text('You have two abilities, melee and fireball.', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                    draw_text('Each ability has a cooldown time.', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 35)
                    draw_text('Melee attacks can hit multiple enemies.', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 60)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.game)]:
                    draw_text('Fight your way through waves of enemies to challange the boss.', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.pause)]:
                    draw_text('You can pause your game anytime by pressing P', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)

        elif stage == stages['starting']:
            draw_text('Wave '+str(wave_number), humongous_font_gothikka, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)
        elif stage == stages['fighting']:
            draw_text('Wave '+str(wave_number), font_gothikka_bold, WHITE,
                      canvas, SCREEN_SIZE[0]//2, 0)
            if boss_fight:
                draw_text('Golem', font_gothikka_bold, WHITE,
                          canvas, SCREEN_SIZE[0]-35, 30)
        elif stage == stages['ending']:
            draw_text('Wave '+str(wave_number) + ' completed', humongous_font_gothikka, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)

        draw_text('You', font_gothikka_bold, WHITE,
                  canvas, 20, 30)
        if paused:
            canvas.blit(dim_screen, (0, 0))
            draw_text('PAUSED', humongous_font_gothikka, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)
        # print(
        #     f'{enemies_to_defeat, len(mobs)} & {total_mobs_per_wave} & {len(entities)} & {remaining_mobs}')
        player.draw_cooldowns(canvas, font_gothikka_bold_numbers)

        window.blit(canvas, (0, 0))
        pygame.display.update()


def main_menu():
    load_music('menu')
    pygame.mixer.music.play(-1, 0.0)
    # menu
    game_button = Button(SCREEN_SIZE[0]//2, 100, 'menu')
    controls_button = Button(SCREEN_SIZE[0]//2, 200, 'menu')
    credits_button = Button(SCREEN_SIZE[0]//2, 300, 'menu')
    quit_button = Button(SCREEN_SIZE[0]//2, 400, 'menu')
    toggle_audio_button = Button(
        SCREEN_SIZE[0] - 50, SCREEN_SIZE[1] - 50, 'audio')
    while True:
        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0
        canvas.fill((0, 0, 0))
        clickable = True
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_m:
                    music_handler.toggle()

        mx, my = pygame.mouse.get_pos()
        if game_button.draw(canvas):
            if clickable:
                clickable = False
                game()
        if controls_button.draw(canvas):
            if clickable:
                clickable = False
                controls()
        if credits_button.draw(canvas):
            if clickable:
                clickable = False
                show_credits()
        if quit_button.draw(canvas):
            if clickable:
                pygame.quit()
                sys.exit()
        if toggle_audio_button.draw(canvas):
            if clickable:
                music_handler.toggle()
                clickable = False

        if music_handler.paused:
            toggle_audio_button.image = pygame.image.load(
                'data/images/button/new/audio_off.png').convert_alpha()
        else:
            toggle_audio_button.image = pygame.image.load(
                'data/images/button/new/audio_on.png').convert_alpha()

        draw_text('Start new game', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 100 + 12)
        draw_text('Controls', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 200 + 12)
        draw_text('Credits', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 300 + 12)
        draw_text('Quit', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 400 + 12)
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
                if event.key == K_m:
                    music_handler.toggle()

        draw_text('Move up', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 100)
        draw_text('W or Arrow up', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 100)
        draw_text('Move down', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 150)
        draw_text('S or Arrow down', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 150)
        draw_text('Move left', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 200)
        draw_text('A or Arrow left', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 200)
        draw_text('Move right', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 250)
        draw_text('D or Arrow right', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 250)
        draw_text('Cast fireball', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 300)
        draw_text('SPACE', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 300)
        draw_text('Melee attack', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 350)
        draw_text('F', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 350)
        draw_text('Pause game', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 400)
        draw_text('P', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 400)
        draw_text('Mute/Unmute sound', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 450)
        draw_text('M', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 450)
        draw_text('Return to menu', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2 - 100, 500)
        draw_text('Escape', font_gothikka_smaller, WHITE,
                  canvas, SCREEN_SIZE[0]//2 + 100, 500)
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
                if event.key == K_m:
                    music_handler.toggle()

        draw_text('Credits', font_gothikka_big, WHITE,
                  canvas, SCREEN_SIZE[0]//2, 100-10)

        window.blit(canvas, (0, 0))
        pygame.display.update()


main_menu()
