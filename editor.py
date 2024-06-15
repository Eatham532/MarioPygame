import os

import pygame
import pygame.freetype
import json
import datetime

from scripts.utils.color import hsl_to_rgb


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

        pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        if mouse[0] and self.tilemap.erase_mode:
            if self.rect.collidepoint(pos):
                self.kill()


class EditorTileMap:
    def __init__(self, game, tile_size=16, name="world"):
        self.tile_size = tile_size
        self.selected_tile = (0, 0)
        self.offset = 0
        self.game = game

        self.scale = 3
        self.window_height = self.game.screen.get_height()
        self.window_width = self.game.screen.get_width()
        self.world_height = round(self.window_height / (self.tile_size * self.scale))
        self.world_width = round(self.window_width / (self.tile_size * self.scale))
        self.world_name = name

        self.tiles = pygame.sprite.Group()
        self.cursor = None

        self.color_id = 0

        self.erase_mode = False
        self.last_saved = None

        self.open(name)

    def save(self, name):
        os.makedirs(f'./assets/worlds/', exist_ok=True)
        f = open(f'./assets/worlds/{name}.json', 'w')
        try:
            data = json.load(f)
        except:
            data = {}

        data["tile_size"] = self.tile_size

        world = []

        for tile in self.tiles:
            world.append({"x": tile.x, "y": tile.y, "color": (tile.fill[0], tile.fill[1], tile.fill[2])})

        data["world"] = world

        print(data)
        self.last_saved = datetime.datetime.now().strftime("%H:%M:%S")
        json.dump([data], f)
        f.close()

    def open(self, name):
        with open(f'./assets/worlds/{name}.json', 'a+') as f:
            print(f'./assets/worlds/{name}.json')
            f.seek(0)

            try:
                data = json.load(f)[0]
            except:
                data = {}

            if not data:
                print("Empty")
                self.world_name = name
                self.tiles.empty()
                f.close()
                return

            self.tile_size = data["tile_size"]

            self.tiles.empty()

            for tile in data["world"]:
                self.tiles.add(Tile(self, tile["x"], tile["y"], self.scale, tile["color"]))

            print(f"Loaded world: {name}")
            print(f"Tile count: {len(self.tiles)}")
            self.world_name = name
            f.close()

    def update(self):
        key = pygame.key.get_pressed()
        key_just = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if self.color_id == 24:
            self.color_id = 0

        x = hsl_to_rgb((self.color_id * 30) / 360, 0.5, 0.6)
        #print(f"RGB values: {x[0] * 255}, {x[1] * 255}, {x[2] * 255}")
        color = pygame.Color(int(x[0] * 255), int(x[1] * 255), int(x[2] * 255))
        #print(f"Color value: {color}")
        #print(f"Color ID: {self.color_id}")

        if self.erase_mode:
            color = (0, 0, 0)

        if key[pygame.K_LEFT]:
            self.offset -= self.tile_size / 2

        if key[pygame.K_RIGHT]:
            self.offset += self.tile_size / 2

        if key_just[pygame.K_SPACE]:
            self.color_id += 1

        if key_just[pygame.K_s]:
            self.save(self.world_name)

        if key_just[pygame.K_o]:
            name = input("Enter the name of the world: ")
            self.open(name)

        if key_just[pygame.K_e]:
            self.erase_mode = not self.erase_mode

        if self.game.screen.get_height() != self.window_height or self.game.screen.get_width() != self.window_width:
            self.window_height = self.game.screen.get_height()
            self.window_width = self.game.screen.get_width()
            self.world_height = round(self.window_height / (self.tile_size * self.scale))
            self.world_width = round(self.window_width / (self.tile_size * self.scale))

        if mouse[0] and not self.erase_mode:
            self.tiles.add(Tile(self, (pos[0] - self.offset) // (self.tile_size * self.scale),
                                pos[1] // (self.tile_size * self.scale),
                                self.scale, color))


        tile_cursor = Tile(self, (pos[0] - self.offset) // (self.tile_size * self.scale), pos[1] //
                           (self.tile_size * self.scale), self.scale, color)
        tile_cursor.update()

        self.cursor = tile_cursor

        self.tiles.update()

    def render(self, screen: pygame.Surface):
        self.tiles.draw(screen)
        self.game.screen.blit(self.cursor.image, [self.cursor.rect.x, self.cursor.rect.y])
        self.game.font.render_to(screen, (10, 10), f"World File: {self.world_name}.json", (255, 255, 255))

        if self.erase_mode:
            self.game.font.render_to(screen, (10, 40), f"ERASE", (255, 0, 0))

        if self.last_saved:
            text = f"Last saved {self.last_saved}"
            text_surface, text_rect = self.game.font.render(text, (0, 0, 0))
            x_position = self.game.screen.get_width() - text_rect.width - 10
            self.game.font.render_to(screen, (x_position, 10), text, (255, 255, 255))

class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1000, 800])
        self.font = pygame.freetype.SysFont("roboto", 24)
        self.dt = None
        self.event_check = []

        self.tile_map = EditorTileMap(self)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        self.dt = 0

        while running:
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    running = False

                for e in self.event_check:
                    e(event, mouse_pos)

            self.screen.fill((0, 0, 0))

            self.tile_map.update()
            self.tile_map.render(self.screen)

            pygame.display.update()
            self.dt = clock.tick(60) / 1000


Editor().run()
