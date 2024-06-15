import pygame
from scripts.entities.entity import Entity


class Player(Entity):
    def __init__(self):
        super().__init__()
        width = 60
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 300
