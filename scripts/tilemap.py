import pygame
import json
import random

from scripts.entities.tile import Tile


class TileMap(pygame.sprite.Group):
    def __init__(self, game, tile_size = 16, length = 10, name = "world"):
        super().__init__()

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

        self.open(name)

    def update(self):
        self.tiles.update()

    def render(self, screen):
        self.tiles.draw(screen)


    def open(self, name):
        with open(f'./assets/worlds/{name}.json', 'r') as f:
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

    def generate_world(self):
        # if not self.world_file:
        #     return
        #
        # next_ = random.randint(0, len(self.world_file.parts))
        #
        # if self.world_file.tile_size:
        #     self.tile_size = self.world_file.tile_size
        #
        # if self.world_file.parts:
        #     if self.world_file.parts["start"]:
        #         self.world.append(self.world_file.parts["start"]["data"])
        #
        #         next_ = self.world_file.parts["start"]["next"]
        #
        #     while len(self.world) < (self.world_len - 1):
        #         part = self.world_file.parts[str(next_)]
        #         self.world.append(part["data"])
        #         next_ = part["next"]
        #
        # if self.world_file.end:
        #     self.world.append(self.world_file.end)
        pass


