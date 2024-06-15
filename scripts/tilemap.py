import pygame
import json
import random


class TileMap(pygame.sprite.Group):
    def __init__(self, game, tile_size = 16, length = 10):
        super().__init__()

        self.tile_size = tile_size
        self.world_len = length
        self.world = []
        self.world_file = None
        self.game = game

    def load(self, filename):
        with open(filename) as f:
            data = json.load(f)
            self.world_file.tile_size = data['tile_size']
            self.world_file.parts = data['world']

    def generate_world(self):
        if not self.world_file:
            return

        next_ = random.randint(0, len(self.world_file.parts))

        if self.world_file.tile_size:
            self.tile_size = self.world_file.tile_size

        if self.world_file.parts:
            if self.world_file.parts["start"]:
                self.world.append(self.world_file.parts["start"]["data"])

                next_ = self.world_file.parts["start"]["next"]

            while len(self.world) < (self.world_len - 1):
                part = self.world_file.parts[str(next_)]
                self.world.append(part["data"])
                next_ = part["next"]

        if self.world_file.end:
            self.world.append(self.world_file.end)


