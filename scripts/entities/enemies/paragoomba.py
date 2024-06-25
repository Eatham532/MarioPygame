import pygame.surface

from scripts.animations import Animatable
from scripts.entities.enemy import Enemy


class Paragoomba(Enemy, Animatable):
    def __init__(self, tilemap, x, y, scale):
        Animatable.__init__(self, "./assets/animations/paragoomba.json")
        self.open()
        self.is_dead = False
        self.size = 16 * scale

        image = pygame.surface.Surface([self.size * scale, self.size * scale])
        Enemy.__init__(self, tilemap, image, x, y)

        self.update_image()


    def update(self):
        if self.is_dead:
            self.sheet_image = self.tilemap.tilesheets["enemies"]
            self.sheet_location = [0, 2]
            self.sheet_name = "enemies"
        else:
            self.update_image()

        self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * self.size,
                                                   self.sheet_location[1] * self.size, self.size,
                                                   self.size))

    def update_image(self):
        current_frame = self.get_current_frame(self.tilemap.game.dt)
        self.sheet_image = self.tilemap.tilesheets[current_frame.image.sheet_name]
        self.sheet_location = [current_frame.image.x, current_frame.image.y]
        self.sheet_name = current_frame.image.sheet_name

