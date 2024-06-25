from scripts.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, tilemap, image, x, y):
        super().__init__(tilemap, x, y, image)

    def move(self):
        pass
