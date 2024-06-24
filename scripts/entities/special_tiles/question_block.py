from scripts.animations import Animatable
from scripts.entities.tile import Tile


class QuestionBlock(Animatable, Tile):
    def __init__(self, tilemap, x, y, scale, p):
        Animatable.__init__(self, "./assets/animations/question_block.json")
        self.open("./assets/animations/question_block.json")
        current_frame = self.get_current_frame(tilemap.game.dt)
        Tile.__init__(self, tilemap, x, y, scale, p,
                      tilemap.tilesheets[current_frame.image.sheet_name],
                      current_frame.image.sheet_name, [current_frame.image.x, current_frame.image.y])

    def update(self):
        current_frame = self.get_current_frame(self.tilemap.game.dt)
        self.sheet_image = self.tilemap.tilesheets[current_frame.image.sheet_name]
        self.sheet_location = [current_frame.image.x, current_frame.image.y]
        self.sheet_name = current_frame.image.sheet_name

        Tile.update(self)

    def hit_below(self):
        print("Question Block hit!")

        if self.property == "boing":
            Tile.hit_below(self)
