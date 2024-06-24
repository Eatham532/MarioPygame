import os

import pygame
import json
import random

from scripts.entities.player import Player
from scripts.entities.tile import Tile
from scripts.utils.special import get_animatable_class_info, get_special_tile_class


class TileMap(pygame.sprite.Group):
    def __init__(self, game, tile_size=16):
        super().__init__()

        self.tile_size = tile_size
        self.offset = 0

        # The scale of the tiles
        self.scale = 3

        # Basic stuff
        self.window_height = game.screen.get_height()
        self.window_width = game.screen.get_width()
        self.world_height = round(self.window_height / (self.tile_size * self.scale))
        self.world_width = round(self.window_width / (self.tile_size * self.scale))
        self.world_name = ""  # The name of the world. Used for getting the saved world

        # The tiles
        self.tiles = pygame.sprite.Group()
        self.player = Player(game)
        game.active_sprite_list.add(self.player)

        # Debugging
        self.outline_tiles = False

        tilesheets_path = "./assets/tilesheets"

        files = os.listdir(tilesheets_path)
        self.tilesheets = {}
        for file in files:
            if file.endswith(".png"):
                path = os.path.join(tilesheets_path, file)
                image = pygame.image.load(path)
                scaled_image = pygame.transform.scale_by(image, self.scale).convert_alpha()
                self.tilesheets[file.strip(".png")] = scaled_image

        self.game = game

    def update(self):
        self.tiles.update()


    def render(self, screen):
        self.game.screen.fill((148, 148, 255))
        self.tiles.draw(screen)


    def open(self, name):
        with open(f'./assets/worlds/{name}.json', 'r') as f:
            print(f'Opening {name} from ./assets/worlds/{name}.json')
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

            # Create the game
            self.tiles.empty()
            for tile in data["world"]:
                if tile["special_tile"]:
                    c = get_special_tile_class(tile["sheet_name"])
                    c_ = c(self, tile["x"], tile["y"], self.scale, tile["props"])
                    self.tiles.add(c_)
                else:
                    self.tiles.add(
                        Tile(self, tile["x"], tile["y"], self.scale, tile["props"], self.tilesheets[tile["sheet_name"]],
                             tile["sheet_name"], tile["sheet_pos"]))

            self.player.__init__(self.game)

            print(f"Loaded world: {name}")
            print(f"Tile count: {len(self.tiles)}")
            self.world_name = name
            self.offset = 0
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


