import time

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
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.set_colorkey((1,1,1))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.property = p
        self.tags = tags

        self.bounce = False
        self.bounce_start_time = None
        self.bounce_time = 100
        self.can_bounce = not self.bounce

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

        if self.bounce:
            if self.bounce_start_time == None:
                self.bounce_start_time = time.time()

            if (time.time() - self.bounce_start_time) * 1000 <= self.bounce_time:
                self.rect.y -= 2

            else:
                self.rect.y += 2

                if self.rect.y >= self.y * self.size:
                    self.rect.y = self.y * self.size
                    self.bounce = False
                    self.bounce_start_time = None



        self.image.fill((1,1,1))
        self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * self.size,
                                                   self.sheet_location[1] * self.size, self.size,
                                                   self.size))

        if self.tilemap.outline_tiles:
            rect = create_bordered_rect(self.size, self.size, 1, (0, 0, 0), (255, 255, 255))
            self.image.blit(rect, (0, 0))

    def hit_below(self):
        if "hazard" == self.property:
            self.tilemap.game.kill_player()
            return

        if "boing" == self.property:
            self.bounce = True

        self.play_hit_sound()


    def hit_above(self):
        if "hazard" == self.property:
            self.tilemap.game.kill_player()
            return


    def play_hit_sound(self):
        self.tilemap.game.play_effect("smb_bump")
