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
    def __init__(self, tilemap, x, y, scale, p, sheet_image, sheet_name, sheet_location=None, tags=[]):
        super().__init__()

        self.tilemap = tilemap
        self.scale = scale
        self.size = tilemap.tile_size * self.scale
        self.image = pygame.Surface([self.size, self.size])
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.property = p
        self.tags = tags

        if sheet_location is None:
            sheet_location = [0, 0]
        else: sheet_location = [sheet_location[0], sheet_location[1]]

        self.sheet_image = sheet_image
        self.sheet_location = sheet_location
        self.sheet_name = sheet_name

        self.rect.y = (self.y * self.size)



    def update(self):
        offset = self.tilemap.offset
        self.rect.x = (self.x * self.size) + offset

        if self.rect.x < -self.rect.width or self.rect.x > self.tilemap.window_width + self.rect.width:
            return

        tile_size = 16
        self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * tile_size * self.scale,
                                                   self.sheet_location[1] * tile_size * self.scale, self.size,
                                                   self.size))

        if self.tilemap.outline_tiles:
            rect = create_bordered_rect(self.size, self.size, 1, (0, 0, 0), (255, 255, 255))
            self.image.blit(rect, (0, 0))
