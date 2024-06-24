import pygame

from scripts.entities.entity import Entity


class Player(Entity):
    def __init__(self, game, speed=10, scale=3):
        super().__init__()

        # Sprite
        width = 16 * scale
        height = 16 * scale
        self.image = pygame.Surface([width, height])
        self.image.fill((255, 0, 0))

        self.health = 1

        # Movement
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 300
        self.speed = speed

        # Jumping
        self.vel_y = 0
        self.max_vel_y = speed * 2
        self.gravity = speed * 1.5
        self.is_jumping = False
        self.jump_start = 0
        self.jump_duration = 0
        self.jump_max_duration = 200
        self.in_water = False

        self.game = game

    def jump(self):
        if not self.is_jumping or self.in_water:
            self.is_jumping = True
            self.vel_y = -self.max_vel_y
            self.jump_start = pygame.time.get_ticks()
            self.jump_duration = 0

    def update(self):
        if self.health <= 0:
            if self.kill_animation:
                pass
            else:
                self.kill_dt = self.game.dt
                self.kill_animation = True

        key = pygame.key.get_pressed()
        key_up = pygame.key.get_just_released()
        key_down = pygame.key.get_just_pressed()

        if self.in_water:
            self.vel_y = -self.speed
            self.gravity = self.speed * 0.4

        else:
            self.max_vel_y = self.speed * 2
            self.gravity = self.speed * 1.5

        dx = -self.speed if key[pygame.K_LEFT] else self.speed if key[pygame.K_RIGHT] else 0
        self.rect.x += dx
        for tile in self.check_collisions():
            if tile.property == "water" or tile.property == "background":
                continue



            if dx < 0:
                self.rect.x = tile.rect.x + tile.rect.width
            elif dx > 0:
                self.rect.x = tile.rect.x - self.rect.width


        if (key_down[pygame.K_SPACE] or key_down[pygame.K_UP]) and (
                self.jump_duration < self.jump_max_duration or self.in_water):
            self.jump()


        if (self.is_jumping and self.jump_duration < self.jump_max_duration):
            self.jump_duration = pygame.time.get_ticks() - self.jump_start

            if key[pygame.K_SPACE] or key[pygame.K_UP]:
                if self.jump_duration < self.jump_max_duration / 2:
                    self.vel_y += self.max_vel_y / 20

            else:
                self.jump_duration *= 2

            if self.vel_y >= self.max_vel_y:
                self.vel_y = self.max_vel_y

            self.rect.y += self.vel_y
        else:
            if self.in_water and self.jump_duration > self.jump_max_duration:
                self.is_jumping = False
                self.jump_duration = 0

                # if key[pygame.K_SPACE] or key[pygame.K_UP]:
                #     self.jump()
            if key[pygame.K_DOWN]:
                self.rect.y += self.gravity * 1.5

            self.vel_y = 0
            self.rect.y += self.gravity

        touching_water = False
        tile_collisions = self.check_collisions()
        hit = False
        for tile in tile_collisions:
            if tile.property == "background":
                continue

            if tile.property == "water":
                touching_water = True
                continue

            if tile.property == "collectable":
                tile.hit_below()
                continue


            if self.vel_y < 0:
                if tile.rect.x < self.rect.centerx < tile.rect.x + tile.rect.width or len(tile_collisions) == 1:
                    tile.hit_below()
                elif self.rect.x == tile.rect.centerx and not hit:
                    tile.hit_below()
                    hit = True

                self.rect.y = tile.rect.y + tile.rect.height
                self.jump_duration = self.jump_max_duration
            else:
                tile.hit_above()
                self.rect.y = tile.rect.y - self.rect.height
                self.is_jumping = False
                self.jump_duration = 0

        del tile_collisions
        del hit

        self.in_water = touching_water

        if self.rect.x > (self.game.tile_map.window_width / 2):
            self.game.tile_map.offset -= self.speed
            self.rect.x -= self.speed

        if self.rect.x < self.speed * 3:
            self.game.tile_map.offset += self.speed
            self.rect.x += self.speed

        if self.rect.y > self.game.tile_map.window_height:
            self.game.set_game_state(3)

        if key[pygame.K_k]:
            self.game.set_game_state(3)

    def check_collisions(self):
        def check_property(tile):
            if tile.property in ["solid", "hazard", "water"]:
                return True
            return False

        tiles = pygame.sprite.spritecollide(self, self.game.tile_map.tiles, False)
        return tiles
