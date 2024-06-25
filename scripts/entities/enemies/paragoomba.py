import pygame.surface

from scripts.animations import Animatable
from scripts.entities.enemy import Enemy
from scripts.entities.tile import Tile


class Paragoomba(Enemy, Animatable):
    def __init__(self, tilemap, x, y, scale):
        Animatable.__init__(self, "./assets/animations/paragoomba.json")
        self.open()
        self.is_dead = False
        self.speed = 1
        self.gravity = self.speed * 3
        self.in_water = False

        size = 16 * scale
        image = pygame.surface.Surface([size, size], pygame.SRCALPHA)
        Enemy.__init__(self, tilemap, image, x, y, size)
        self.facing_left = True

        self.update_image()

    def update(self):
        self.move()
        super().update()

        if self.rect.x > self.tilemap.window_width + 100 or self.rect.x < -100:
            return

        if not self.is_dead:
            self.update_image()
            self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * self.size,
                                                       self.sheet_location[1] * self.size, self.size,
                                                       self.size))
        else:
            self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * self.size,
                                                       self.sheet_location[1] * self.size / 2, self.size,
                                                       self.size / 2))





    def move(self):
        if self.is_dead:
            self.rect.y += self.speed * 3
            if self.rect.y >= self.tilemap.window_height:
                self.kill()

            return

        if self.in_water:
            self.gravity = self.speed
        else:
            self.gravity = self.speed * 3

        in_water = False
        self.rect.y += self.gravity
        collide = False
        group = pygame.sprite.spritecollide(self, self.tilemap.tiles, False)
        for tile in group:
            if tile.property == "water":
                in_water = True

            if tile.property == "solid" or tile.property == "boing" and isinstance(tile, Tile):
                collide = True

        if collide:
            self.rect.y -= self.gravity
        else:
            return

        if self.facing_left:
            self.move_x -= self.speed
        else:
            self.move_x += self.speed

        collide = False
        group = pygame.sprite.spritecollide(self, self.tilemap.tiles, False)
        for tile in group:
            if tile.property == "water":
                in_water = True

            if tile.property == "solid" or tile.property == "water" or tile.property == "boing" and isinstance(tile, Tile):
                collide = True


        if collide:
            if self.facing_left:
                self.move_x += self.speed * 2 + 1
            else:
                self.move_x -= self.speed * 2 + 1
            self.facing_left = not self.facing_left



        self.in_water = in_water

    def update_image(self):
        current_frame = self.get_current_frame(self.tilemap.game.dt)
        self.sheet_image = self.tilemap.tilesheets[current_frame.image.sheet_name]
        self.sheet_location = [current_frame.image.x, current_frame.image.y]
        self.sheet_name = current_frame.image.sheet_name


    def hit_above(self):
        if not self.is_dead:
            self.is_dead = True
            x, y = self.rect.topleft
            self.image = pygame.surface.Surface([self.size, self.size / 2], pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

            self.sheet_image = self.tilemap.tilesheets["enemies"]
            self.sheet_location = [2, 0]
            self.sheet_name = "enemies"
            self.property = "background"

