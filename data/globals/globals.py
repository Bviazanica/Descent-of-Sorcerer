
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


CAMERA_TOP, CAMERA_BOTTOM = -268, 746
LEFT_BORDER, RIGHT_BORDER = -380, 1500
TOP_BORDER, BOTTOM_BORDER = 120, 640


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


# animation_types = ['Idle', 'Running', 'Dying']
#         # load all images for the players
#         for animation in animation_types:
#             # reset temporary list of images
#             temp_list = []
#             # count number of files in the folder
#             num_of_frames = len(os.listdir(
#                 f'data/images/entities/{self.type}/{animation}'))
#             for i in range(num_of_frames):
#                 img = pygame.image.load(
#                     f'data/images/entities/{self.type}/{animation}/{i}.png')
#                 img = pygame.transform.scale(img, (64, 128))
#                 temp_list.append(img)
#             self.animation_list.append(temp_list)
