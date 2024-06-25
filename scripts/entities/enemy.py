from scripts.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, tilemap, image, x, y, size):
        super().__init__(tilemap, x * size, y * size, image)
        self.property = "enemy"
        self.size = size
        self.x = x
        self.y = y
        self.move_x = 0

    def update(self):
        offset = self.tilemap.offset
        self.rect.x = (self.x * self.size) + offset + self.move_x


    def move(self):
        pass

    def hit_above(self):
        pass

    def hit_below(self):
        pass
