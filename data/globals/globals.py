
from enum import IntEnum

FPS = 60  # frame rate
SCREEN_SIZE = width, height = 800, 600
# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (240, 0, 0)
GREEN = (0, 240, 0)
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
