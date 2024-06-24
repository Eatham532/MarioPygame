from scripts.animations import Animatable
from scripts.entities.tile import Tile


class Coin(Tile, Animatable):
    def __init__(self, tilemap, x, y, scale, p):
        Animatable.__init__(self, "./assets/animations/coin.json")
        self.open("./assets/animations/coin.json")
        current_frame = self.get_current_frame(tilemap.game.dt)
        Tile.__init__(self, tilemap, x, y, scale, "collectable",
                      tilemap.tilesheets[current_frame.image.sheet_name],
                      current_frame.image.sheet_name, [current_frame.image.x, current_frame.image.y])

    def hit_below(self):
        self.hit()

    def hit_above(self):
        self.hit()

    def hit(self):
        self.tilemap.game.coins += 1
        self.tilemap.game.play_effect("smb_coin")
        self.kill()

    def update(self):
        current_frame = self.get_current_frame(self.tilemap.game.dt)
        self.sheet_image = self.tilemap.tilesheets[current_frame.image.sheet_name]
        self.sheet_location = [current_frame.image.x, current_frame.image.y]
        self.sheet_name = current_frame.image.sheet_name

        Tile.update(self)