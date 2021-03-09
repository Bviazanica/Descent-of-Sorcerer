import pygame
import pygame_ai as pai


class CircleNPC(pai.gameobject.GameObject):

    def __init__(self, pos=(100, 100)):
        # First create the circle image with alpha channel to have transparency
        img = pygame.Surface((10, 10)).convert_alpha()
        img.fill((255, 255, 255, 0))
        # Draw the circle
        pygame.draw.circle(img, (0, 130, 255), (5, 5), 5)
        # Call GameObejct init with appropiate values
        super(CircleNPC, self).__init__(
            img_surf=img,
            pos=pos,
            max_speed=25,
            max_accel=20,
            max_rotation=40,
            max_angular_accel=20
        )
        # Create a placeholder for the AI
        self.ai = pai.steering.kinematic.NullSteering()

    def update(self, tick):
        steering = self.ai.get_steering()
        self.steer(steering, tick)
        self.rect.move_ip((int(self.velocity[0]), int(self.velocity[1])))
        print(self.rect)
