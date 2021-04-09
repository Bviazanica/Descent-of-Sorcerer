import pygame
from data.globals.globals import *


class Pause(object):

    def __init__(self):
        self.paused = pygame.mixer.music.get_busy()

    def toggle(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.set_all_sounds_volume(0.5)

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
        if not self.paused:
            pygame.mixer.music.pause()
            self.mute_all_sound_effect()
        self.paused = not self.paused

        return True

    def mute_all_sound_effect(self):
        for sound in sound_effects:
            pygame.mixer.Sound.set_volume(sound, 0.0)

    def set_all_sounds_volume(self, float_value):
        for sound in sound_effects:
            pygame.mixer.Sound.set_volume(sound, float_value)
