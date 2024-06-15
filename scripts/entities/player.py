import pygame
from scripts.entities.entity import Entity


class Player(Entity):
    def __init__(self, game, speed=10):
        super().__init__()
        width = 60
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 300
        self.speed = speed

        self.vel_y = 0
        self.max_vel_y = speed * 2
        self.gravity = speed * 2
        self.is_jumping = False
        self.jump_start = 0
        self.jump_duration = 0
        self.jump_max_duration = 200

        self.game = game

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -self.max_vel_y
            self.jump_start = pygame.time.get_ticks()


    def update(self):
        key = pygame.key.get_pressed()
        key_up = pygame.key.get_just_released()
        key_down = pygame.key.get_just_pressed()

        if key[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.collides_with_tiles():
                self.rect.x = self.colliding_tile.rect.x + self.colliding_tile.rect.width

        if key[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.collides_with_tiles():
                self.rect.x = self.colliding_tile.rect.x - self.rect.width

        if (key_down[pygame.K_SPACE] or key_down[pygame.K_UP]) and self.jump_duration < self.jump_max_duration:
            self.jump()


        if self.is_jumping and self.jump_duration < self.jump_max_duration:
            self.jump_duration = pygame.time.get_ticks() - self.jump_start

            if (key[pygame.K_SPACE] or key[pygame.K_UP]):
                if self.jump_duration < self.jump_max_duration / 2:
                    self.vel_y += self.max_vel_y / 20
            else:
                self.jump_duration *= 2


            if self.vel_y >= self.max_vel_y:
                self.vel_y = self.max_vel_y



            self.rect.y += self.vel_y

            if self.collides_with_tiles():
                self.rect.y = self.colliding_tile.rect.y + self.colliding_tile.rect.height
                self.jump_duration = self.jump_max_duration
        else:
            self.vel_y = 0
            self.rect.y += self.gravity

        if self.collides_with_tiles():
            self.rect.y = self.colliding_tile.rect.y - self.rect.height
            self.is_jumping = False
            self.jump_duration = 0

        if self.rect.x > (self.game.tile_map.window_width / 2):
            self.game.tile_map.offset -= self.speed
            self.rect.x -= self.speed

        if self.rect.x < self.speed * 3:
            self.game.tile_map.offset += self.speed
            self.rect.x += self.speed




    def collides_with_tiles(self):
        for tile in self.game.tile_map.tiles:
            if self.rect.colliderect(tile.rect):
                self.colliding_tile = tile
                return True
        self.colliding_tile = None
        return False
