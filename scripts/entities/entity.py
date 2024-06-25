import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, tilemap, x, y, image):
        super().__init__()
        self.tilemap = tilemap
        self.image = image
        self.rect = image.get_rect()

        self.rect.x = x
        self.rect.y = y


    def move(self):
        pass

    def update(self):
        self.move()

    def hit(self):
        self.kill()
