import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, tilemap, x, y, scale, color=(255, 0, 0), tags=[]):
        super().__init__()

        self.tilemap = tilemap
        self.scale = scale
        self.size = tilemap.tile_size * self.scale
        self.image = pygame.Surface([self.size, self.size])
        self.fill = color
        self.image.fill(self.fill)
        self.rect = self.image.get_rect()
        self.offset = tilemap.offset
        self.x = x
        self.y = y
        self.tags = tags



    def update(self):
        self.offset = self.tilemap.offset
        self.rect.x = (self.x * self.size) + self.offset
        self.rect.y = (self.y * self.size)

        self.image.fill(self.fill)