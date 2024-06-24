import random

from scripts.entities.tile import Tile


class CoinBlock(Tile):
    def __init__(self, tilemap, x, y, scale, p):
        super().__init__(tilemap, x, y, scale, "boing", tilemap.tilesheets["tiles"], "tiles", [1, 0])
        self.coin_count = random.randint(1, 5)
        self.coins_given = 0

    def hit_below(self):
        super().hit_below()

        if not self.coins_given >= self.coin_count:
            self.tilemap.game.coins += 1
            self.coins_given += 1

            if self.coins_given >= self.coin_count:
                self.sheet_location = [3, 0]
                self.property = "solid"


    def play_hit_sound(self):
        if self.sheet_location == [1, 0]:
            self.tilemap.game.play_effect("smb_coin")
        else:
            self.tilemap.game.play_effect("smb_bump")
