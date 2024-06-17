import pygame


def create_bordered_rect(width, height, border_thickness, fill_color, border_color):
    # Create a surface with extra space for the border
    surf = pygame.Surface((width + border_thickness * 2, height + border_thickness * 2), pygame.SRCALPHA)

    # Draw the inner rectangle
    pygame.draw.rect(surf, fill_color, (border_thickness, border_thickness, width, height))

    # Draw the outer border
    for i in range(border_thickness):
        pygame.draw.rect(surf, border_color,
                         (border_thickness - i, border_thickness - i, width + i * 2, height + i * 2))

    return surf

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

        if self.tilemap.outline_tiles:
            rect = create_bordered_rect(self.size, self.size, 1, (0, 0, 0), (255, 255, 255))
            self.image.blit(rect, (0, 0))
