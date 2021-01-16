import pygame

size = width, height = 800, 600
black = 0, 0, 0

# initialize the pygame
pygame.init()

# create the canvas
screen = pygame.display.set_mode(size)
running = True

# Title
pygame.display.set_caption("Celestial")


# Game Loop
while running:
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

