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
from data.cut_scenes import CutSceneManager

# window & canvas
window = pygame.display.set_mode(SCREEN_SIZE)
canvas = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))
# setup
clock = pygame.time.Clock()
pygame.init()
pygame.mixer.init(48000,  16, 2, 4096, 'Name', 0)

# load animations
entities_animation_list = load_entity_animations()
projectiles_animation_list = load_projectile_animations()
spells_animation_list = load_spells_animations()

# Titles
pygame.display.set_caption("Descent of Sorcerer")
icon = pygame.image.load(
    f'data/images/icons/game.png').convert_alpha()
pygame.display.set_icon(icon)
pygame.mouse.set_cursor(*pygame.cursors.tri_left)
# background
background = pygame.image.load(
    'data/images/backgrounds/background.png').convert_alpha()
front_decor = pygame.image.load(
    'data/images/backgrounds/front_decor.png').convert_alpha()
bgWidth = background.get_width()
bgHeight = background.get_height()
# dim screen
dim_screen = pygame.Surface(window.get_size()).convert_alpha()
dim_screen.fill((0, 0, 0, 180))
tutorial_text = pygame.Surface((window.get_width(), 100)).convert_alpha()
tutorial_text.fill((0, 0, 0, 180))

# upgrade images
fireball_icon = (pygame.image.load(
    'data/images/icons/fireball_big_icon.jpg')).convert_alpha()
staff_icon = pygame.image.load(
    'data/images/icons/staff_big_icon.jpg').convert_alpha()
lightning_icon = pygame.image.load(
    'data/images/icons/lightning_big_icon.jpg').convert_alpha()
decoy_icon = pygame.image.load(
    'data/images/icons/decoy_big_icon.jpg').convert_alpha()

#health and mana
health_icon = pygame.image.load(
    'data/images/icons/health_icon.png').convert_alpha()
mana_icon = pygame.image.load(
    'data/images/icons/mana_icon.png').convert_alpha()

health_icon = pygame.transform.smoothscale(health_icon, (25, 25))
mana_icon = pygame.transform.smoothscale(mana_icon, (15, 22))

arrow_button = pygame.image.load('data/images/button/arrow.png').convert_alpha()
main_button = pygame.image.load('data/images/button/button.png').convert_alpha()
audio_on_button = pygame.image.load('data/images/button/audio_on.png').convert_alpha()
audio_off_button = pygame.image.load('data/images/button/audio_off.png').convert_alpha()

arrow_button = pygame.transform.smoothscale(arrow_button, (40, 30))
main_button = pygame.transform.smoothscale(main_button, (200,50))
audio_on_button = pygame.transform.smoothscale(audio_on_button, (30,30))
audio_off_button = pygame.transform.smoothscale(audio_off_button, (30,30))
# states of game
stages = {'tutorial': 'tutorial', 'starting': 'starting',
          'fighting': 'fighting', 'ending': 'ending', 'upgrading': 'upgrading', 'discovering': 'discovering', 'finish': 'finish'}
# mechanics in tutorial
tutorial_stages = ['movement',  'attacks', 'game', 'pause']

tutorial = True
clickable = True
two_seconds_timer = 2000
# music volume and sounds volume
pygame.mixer.music.set_volume(0.1)
music_handler = Pause()
music_handler.set_all_sounds_volume(0.5)


# main game
def game():
    global arrow_button
    global restart_button
    global main_button
    # game initionalization
    load_music('main_background')
    if not music_handler.paused:
        pygame.mixer.music.play(-1, 0.0)

    available_skills = [fireball_icon, staff_icon]
    skills_icons = upgrade_options(available_skills)
    entities = []
    items = []
    mobs = []
    player = Player(400, 200, entities_animation_list)
    entities.append(player)
    camera = Camera(player)
    border = Border(camera, player)
    camera.setmethod(border)
    death_screen_running = False
    boss_fight = False
    running = True
    paused = False
    current_time = 0
    time_before_pause = 0
    enemies_to_defeat = 0
    wave_number = 0
    final_wave = 25
    spawn_mobs_number = 4
    total_mobs_per_wave = 2
    max_spawn_mobs_number = 8
    last_spawned_time = 0
    start_upgrade_after_wave = 5
    stage_loading_time = 3000
    spawn_cooldown = 15000
    remaining_mobs = 0
    tutorial_text.fill((0, 0, 0, 180))
    boss = []
    amount = 50
    discover_started = 0
    global tutorial

    # cut scenes
    cut_scene_manager = CutSceneManager(canvas)

    next_button = Button(
        SCREEN_SIZE[0] - 25, SCREEN_SIZE[1] - 25, 'arrow', arrow_button)
    restart_button = Button(SCREEN_SIZE[0]//2, 300, 'menu', main_button)
    menu_button = Button(SCREEN_SIZE[0]//2, 400, 'menu', main_button)

    if tutorial:
        tutorial = False
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
        time_passed = clock.tick(FPS)
        time_passed_seconds = time_passed / 1000.0
        canvas.fill(BLACK)
        current_time += time_passed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # keybinds
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
                    death_screen_running = True
                    load_music('death_screen')
                    if not music_handler.paused:
                        pygame.mixer.music.play(-1, 0.0)

                    # gameover screen loop
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
                        # restart game
                        if restart_button.draw(canvas):
                            if clickable:
                                menu_select_sound.play()
                                entities = []
                                items = []
                                mobs = []

                                player = Player(400, 200, entities_animation_list)
                                entities.append(player)

                                camera = Camera(player)
                                border = Border(camera, player)
                                camera.setmethod(border)
                                amount = 50
                                current_time = 0
                                time_before_pause = 0
                                player.death_screen_ready = False
                                death_screen_running = False
                                stage = stages['starting']
                                new_stage = True
                                stage_start = 0
                                wave_number = 0
                                boss_fight = False
                                enemies_to_defeat = 2
                                spawn_mobs_number = 4
                                total_mobs_per_wave = 2
                                last_spawned_time = 0
                                load_music('main_background')
                                available_skills = [fireball_icon, staff_icon]
                                skills_icons = upgrade_options(
                                    available_skills)
                                if not music_handler.paused:
                                    pygame.mixer.music.play(-1, 0.0)
                                clickable = False
                                # cut scenes
                                cut_scene_manager = CutSceneManager(canvas)
                        # return to menu from game over screen
                        if menu_button.draw(canvas):
                            if clickable:
                                menu_select_sound.play()
                                player.death_screen_ready = False
                                death_screen_running = False
                                running = False
                                load_music('menu')
                                if not music_handler.paused:
                                    pygame.mixer.music.play(-1, 0.0)
                                clickable = False
                        if stage == stages['finish']:
                            draw_text('Congratulations', humongous_font_gothikka, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 100)
                            draw_text("You've made it", font_gothikka_big, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 200)
                            draw_text('Start new game', font_gothikka, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 285)
                        else:
                            draw_text('Game over', humongous_font_gothikka, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 100)
                            draw_text('You have reached wave '+str(wave_number), font_gothikka_big, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 200)
                            draw_text('Restart', font_gothikka, WHITE,
                                      canvas, SCREEN_SIZE[0]//2, 285)

                        draw_text('Back to menu', font_gothikka, WHITE,
                                  canvas, SCREEN_SIZE[0]//2, 385)
                        window.blit(canvas, (0, 0))
                        pygame.display.update()

            else:
                # Starting stage
                if stage == stages['starting']:
                    if new_stage:
                        stage_loading_time = 5000
                        wave_number += 1
                        boss_fight = False
                        if wave_number % 5 == 0:
                            boss_fight = True
                            amount += 5
                        else:
                            total_mobs_per_wave += 2
                            enemies_to_defeat = total_mobs_per_wave
                        stage_start = current_time
                        new_stage = False

                    if current_time - stage_start > stage_loading_time:
                        stage = stages['fighting']
                        new_stage = True
                # fighting stage
                elif stage == stages['fighting']:
                    # boss wave
                    if boss_fight:
                        if new_stage:
                            boss = Boss(400, -420, entities_animation_list)
                            boss.desired_appear = Vector2(
                                boss.rect.centerx, 100)
                            upgrade_boss(boss, wave_number)
                            entities.append(boss)
                            new_stage = False
                            if spawn_mobs_number < max_spawn_mobs_number:
                                spawn_mobs_number += 2
                        if len(mobs) < 1 and not boss.is_alive:
                            if wave_number != final_wave:
                                stage = stages['ending']
                            else:
                                stage = stages['finish']
                                pygame.mixer.music.stop()
                                win_sound.play()
                            new_stage = True
                            boss_fight = False
                    elif new_stage:
                        last_spawned_time = current_time
                        spawn_coords_x = random.choice([-450, 930])
                        desired_coords_offset = 100
                        if spawn_coords_x > 0:
                            desired_coords_offset *= -1
                        new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number,
                                          wave_number, desired_coords_offset, True, start_upgrade_after_wave, entities_animation_list)
                        new_stage = False
                        mobs.extend(new_mobs)
                        entities.extend(new_mobs)
                    # normal wave
                    elif not boss_fight:
                        spawn_coords_x = random.choice([-450, 930])
                        desired_coords_offset = 100
                        if spawn_coords_x > 0:
                            desired_coords_offset *= -1
                        remaining_mobs = enemies_to_defeat - len(mobs)

                        if len(mobs) < 1 and enemies_to_defeat > 0:
                            if enemies_to_defeat >= spawn_mobs_number:
                                last_spawned_time = current_time

                                new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number,
                                                  wave_number, desired_coords_offset, True, start_upgrade_after_wave, entities_animation_list)
                            elif enemies_to_defeat >= spawn_mobs_number//2:
                                last_spawned_time = current_time
                                new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number//2,
                                                  wave_number, desired_coords_offset, True, start_upgrade_after_wave, entities_animation_list)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        elif remaining_mobs >= spawn_mobs_number and current_time - last_spawned_time > spawn_cooldown:
                            last_spawned_time = current_time

                            new_mobs = summon(Enemy, spawn_coords_x, 50, spawn_mobs_number,
                                              wave_number, desired_coords_offset, True, start_upgrade_after_wave, entities_animation_list)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        elif remaining_mobs < spawn_mobs_number and remaining_mobs > 0 and current_time - last_spawned_time > spawn_cooldown:
                            last_spawned_time = current_time

                            new_mobs = summon(Enemy, spawn_coords_x, 50, remaining_mobs,
                                              wave_number, desired_coords_offset, True, start_upgrade_after_wave, entities_animation_list)
                            mobs.extend(new_mobs)
                            entities.extend(new_mobs)
                        if enemies_to_defeat < 1 and len(mobs) < 1:
                            stage = stages['ending']
                            new_stage = True
                # ending stage
                elif stage == stages['ending']:
                    if new_stage:
                        stage_start = current_time
                        wave_complete_sound.play()
                        new_stage = False
                    # determine when to upgrade skill
                    if current_time - stage_start > stage_loading_time and not player.boosted:
                        if wave_number % 5 == 0:
                            stage = stages['upgrading']
                            new_stage = True
                            paused = True
                        # go to starting state again
                        else:
                            stage = stages['starting']
                            new_stage = True

                # movement
                if stage != stages['finish']:
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

                    # player actions & attack states
                    if (pressed_keys[K_d] or pressed_keys[K_a] or pressed_keys[K_s] or pressed_keys[K_w]
                            or pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_UP] or pressed_keys[K_DOWN]) and player.init_state and player.state != player.states['HURTING']:
                        player.state = player.states['RUNNING']

                    if pressed_keys[K_SPACE] and player.mana_points >= player.mana_costs['fireball'] and get_cooldown_ready(player.fireball_time, player.cooldowns['fireball'], current_time):
                        player.casting = 'fireball'
                        if player.state == 'RUNNING':
                            player.state = player.states['RUNNING-FIRING']
                        else:
                            player.state = player.states['FIRING']
                    elif player.lightning_learned and pressed_keys[K_c] and player.mana_points >= player.mana_costs['lightning'] and get_cooldown_ready(player.lightning_time, player.cooldowns['lightning'], current_time):
                        player.casting = 'lightning'
                        if player.state == 'RUNNING':
                            player.state = player.states['RUNNING-FIRING']
                        else:
                            player.state = player.states['FIRING']
                    elif player.decoy_learned and pressed_keys[K_v] and player.mana_points >= player.mana_costs['decoy'] and get_cooldown_ready(player.decoy_time, player.cooldowns['decoy'], current_time):
                        player.casting = 'decoy'
                        if player.state == 'RUNNING':
                            player.state = player.states['RUNNING-FIRING']
                        else:
                            player.state = player.states['FIRING']

                    if pressed_keys[K_f] and current_time - player.melee_attack_time > player.cooldowns['melee']:
                        if player.state == 'RUNNING':
                            player.state = player.states['RUNNING-ATTACKING']
                        else:
                            player.state = player.states['ATTACKING']

                    # player idling
                    if not pressed_keys.count(1) and player.state != player.states['HURTING'] and player.state != player.states['DYING']:
                        player.state = player.states['IDLING']

                    movement.normalize()
            # update methods for entities
            for entity in entities:
                if entity.type == 'decoy':
                    entity.update(current_time, entities)
                elif entity.type == 'player':
                    entity.update(current_time, time_passed_seconds, movement,
                                  entities, stage, cut_scene_manager, entities_animation_list,projectiles_animation_list,spells_animation_list)
                    if entity.entities_summoned:
                        new_decoys = entity.get_summoned_entities()
                        entities.extend(new_decoys)
                        entity.entities_summoned = False
                elif entity.type == 'boss':
                    entity.update(player, current_time, time_passed_seconds, movement,
                                  entities, Enemy, stage, wave_number, start_upgrade_after_wave, projectiles_animation_list,entities_animation_list)
                    if entity.entities_summoned:
                        boss_summons = entity.get_summoned_entities()
                        enemies_to_defeat = len(boss_summons)
                        mobs.extend(boss_summons)
                        entities.extend(boss_summons)
                        entity.entities_summoned = False
                elif entity.type == 'mob':
                    entity.update(current_time, time_passed_seconds, player,
                                  get_entities_to_avoid(entities), stage, boss, entities)
            cut_scene_manager.update(current_time, time_passed_seconds)
            # clearing defeated mob entities
            for mob in mobs.copy():
                if not mob.is_alive and mob.init_state:
                    mobs.pop(mobs.index(mob))
            # clearing defeated en
            for entity in entities.copy():
                if not entity.is_alive and entity.init_state and entity.type != 'player':
                    if entity.type == 'mob':
                        enemies_to_defeat -= 1
                        chance = random.random()
                        if chance < 0.25:
                            new_potion = None
                            if chance < 0.10:
                                new_potion = Potion('health', entity.hitbox.midbottom, 32, 32)
                            elif chance < 0.17:
                                new_potion = Potion('mana', entity.hitbox.midbottom, 32, 32)
                            elif chance < 0.21:
                                new_potion = Potion('invulnerability', entity.hitbox.midbottom, 32, 32)
                                items.append(new_potion)
                            else:
                                new_potion = Potion('power', entity.hitbox.midbottom, 32, 32)
                            items.append(new_potion)
                    entities.pop(entities.index(entity))

            # potions and their effects
            items_collisions = check_collision(player.hitbox, items)
            for item in items_collisions:
                if item.name == 'health':
                    item.heal(player, items, amount)
                elif item.name == 'mana':
                    item.regenerate_mana(player, items, amount)
                elif item.name == 'power':
                    item.boost(player, items, current_time)
                elif item.name == 'invulnerability':
                    item.invulnerability(player, items, current_time)
            # adjust camera to player
            camera.scroll()

        canvas.blit(background, (int(0 - camera.offset.x +
                                     camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))

        # draw potions
        for item in items:
            item.draw(canvas, camera.offset.x, camera.offset.y)

        # sort entities by Y position, from the lowest to highest for illusion of space
        sorted_entities = sorted(
            entities, key=lambda x: x.hitbox.bottom, reverse=False)

        # draw sorted entities
        for entity in sorted_entities:
            entity.draw(canvas, camera.offset.x, camera.offset.y, player)

        canvas.blit(health_icon, (5, 6))
        canvas.blit(mana_icon, (5, 29))
        # tutorial stage
        if stage == stages['tutorial']:
            canvas.blit(front_decor, (int(0 - camera.offset.x +
                                          camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
            player.draw_cooldowns(canvas, font_gothikka_bold_numbers)
            canvas.blit(tutorial_text, (0, SCREEN_SIZE[1] - 100))

            if next_button.draw(canvas):
                if tutorial_stage_index == len(tutorial_stages)-1:
                    stage = stages['starting']
                    new_stage = True
                    tutorial_text.fill((0, 0, 0, 180))
                else:
                    tutorial_stage_index += 1
                    tutorial_stage = tutorial_stages[tutorial_stage_index]
                    new_tutorial_stage = True
                    tutorial_text.fill((0, 0, 0, 180))
                next_click_sound.play()

            if new_tutorial_stage:
                new_tutorial_stage = False
                if tutorial_stage == tutorial_stages[int(Tutorial_stage.movement)]:
                    draw_text('Move with W,A,S,D or with arrow keys on your keyboard', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                elif tutorial_stage == tutorial_stages[int(Tutorial_stage.attacks)]:
                    draw_text('To cast a fireball press Space', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                    draw_text('For melee attack press F', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 35)
                elif tutorial_stage == tutorial_stages[int(Tutorial_stage.game)]:
                    draw_text('Fight your way through waves of enemies to challange the boss', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                    draw_text('Beat as many waves as you can', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 35)
                elif tutorial_stage == tutorial_stages[int(Tutorial_stage.pause)]:
                    draw_text('You can pause your game anytime by pressing P', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 10)
                    draw_text('You can also mute sounds and music by pressing M or you can do it in main menu', font_gothikka, WHITE,
                              tutorial_text, SCREEN_SIZE[0]//2, 35)

        elif stage == stages['starting']:
            draw_text('Wave '+str(wave_number), humongous_font_gothikka, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)
        elif stage == stages['fighting']:
            draw_text('Wave '+str(wave_number), font_gothikka_bold, WHITE,
                      canvas, SCREEN_SIZE[0]//2, 0)
        elif stage == stages['ending']:
            draw_text('Wave '+str(wave_number) + ' completed', humongous_font_gothikka, WHITE,
                      canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 - 100)

        # discover stage
        elif stage == stages['discovering']:
            canvas.blit(front_decor, (int(0 - camera.offset.x +
                                          camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
            if current_time - discover_started > two_seconds_timer:
                canvas.blit(tutorial_text, (0, SCREEN_SIZE[1] - 100))
                if new_stage:
                    stage_start = current_time
                    stage_loading_time = 10000
                    tutorial_text.fill((0, 0, 0, 180))
                    ability_learn_sound.play()
                    new_stage = False
                    if wave_number == 5:
                        available_skills.append(lightning_icon)
                        player.spells_icons.append(player.lightning_icon)
                        player.lightning_learned = True
                        draw_text('You have discovered a new ability - Lightning bolt', font_gothikka, WHITE,
                                  tutorial_text, SCREEN_SIZE[0]/2, 10)
                        draw_text('To cast Lightning bolt press C', font_gothikka, WHITE,
                                  tutorial_text, SCREEN_SIZE[0]/2, 35)
                    elif wave_number == 10:
                        available_skills.append(decoy_icon)
                        player.spells_icons.append(player.decoy_icon)
                        player.decoy_learned = True
                        draw_text('You have discovered a new ability - Explosive decoy', font_gothikka, WHITE,
                                  tutorial_text, SCREEN_SIZE[0]/2, 10)
                        draw_text('To cast Explosive decoy press V', font_gothikka, WHITE,
                                  tutorial_text, SCREEN_SIZE[0]/2, 35)
                    skills_icons = upgrade_options(available_skills)

                if current_time - stage_start > stage_loading_time:
                    stage = stages['starting']
                    new_stage = True

            player.draw_cooldowns(canvas, font_gothikka_bold_numbers)
        # cooldown and front decor on top layer
        if stage != stages['tutorial'] and stage != stages['discovering']:
            canvas.blit(front_decor, (int(0 - camera.offset.x +
                                          camera.CONST[0]), int(0 - camera.offset.y + camera.CONST[1])))
            player.draw_cooldowns(canvas, font_gothikka_bold_numbers)

        # if upgrading skill or game is paused, cds on top layer
        if paused:
            canvas.blit(dim_screen, (0, 0))
            if stage == stages['upgrading']:
                if new_stage:
                    upgrade_abilities_sound.play()
                    clickable = True
                    new_stage = False
                draw_text('Choose ability to upgrade', humongous_font_gothikka,
                          WHITE, canvas, SCREEN_SIZE[0]//2, 100)
                for skill in skills_icons:
                    pygame.draw.rect(canvas, BLACK,
                                     (skill.rect.x, skill.rect.y, skill.rect.width, skill.rect.height), 5)
                    if skill.draw(canvas):
                        if clickable:
                            upgrade_skill(skills_icons.index(skill), player)
                            clickable = False
                            paused = False
                            new_stage = True
                            upgrade_sound.play()
                            if wave_number == 5 or wave_number == 10:
                                stage = stages['discovering']
                                discover_started = current_time
                            else:
                                stage = stages['starting']

            else:
                draw_text('PAUSED', humongous_font_gothikka, WHITE,
                          canvas, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)

        cut_scene_manager.draw(font_gothikka_bold)
        if running:
            window.blit(canvas, (0, 0))
            pygame.display.update()


def main_menu():
    global main_button
    global audio_on_button
    global audio_off_button
    load_music('menu')
    pygame.mixer.music.play(-1, 0.0)
    # menu
    game_button = Button(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.5, 'menu', main_button)
    controls_button = Button(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.6, 'menu', main_button)
    credits_button = Button(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.7, 'menu', main_button)
    quit_button = Button(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.8, 'menu', main_button)
    toggle_audio_button = Button(
        SCREEN_SIZE[0] - 50, SCREEN_SIZE[1] - 50, 'audio', audio_on_button)
    audio_state_changed = False
    clickable = False
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
                menu_select_sound.play()
                clickable = False
                game()
        draw_text('Start new game', font_gothikka, WHITE,
                  canvas, game_button.rect.centerx, game_button.rect.y + 10)
        
        if controls_button.draw(canvas):
            if clickable:
                menu_select_sound.play()
                clickable = False
                controls()
        draw_text('Controls', font_gothikka, WHITE,
                  canvas, controls_button.rect.centerx, controls_button.rect.y + 10)
        if credits_button.draw(canvas):
            if clickable:
                menu_select_sound.play()
                clickable = False
                show_credits()
        draw_text('Credits', font_gothikka, WHITE,
                  canvas, credits_button.rect.centerx, credits_button.rect.y + 10)
        if quit_button.draw(canvas):
            if clickable:
                menu_select_sound.play()
                clickable = False
                pygame.quit()
                sys.exit()
        draw_text('Quit', font_gothikka, WHITE,
                  canvas, quit_button.rect.centerx, quit_button.rect.y + 10)
        if toggle_audio_button.draw(canvas):
            if clickable:
                clickable = False
                audio_state_changed = music_handler.toggle()

        if audio_state_changed:
            if music_handler.paused:
                toggle_audio_button.image = audio_off_button

            else:
                toggle_audio_button.image = audio_on_button
            audio_state_changed = False
            clickable = False
        
        draw_text('Descent', font_gothikka_big, WHITE,
                  canvas, SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.1)
        draw_text('of', font_gothikka_big, WHITE,
                  canvas, SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.2)
        draw_text('Sorcerer', font_gothikka_big, WHITE,
                  canvas, SCREEN_SIZE[0]//2, SCREEN_SIZE[1]*0.3)
        
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
                  canvas, SCREEN_SIZE[0]//2, 100)
        draw_text('in progress', font_gothikka, WHITE,
                  canvas, SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2) 
        window.blit(canvas, (0, 0))
        pygame.display.update()


main_menu()
