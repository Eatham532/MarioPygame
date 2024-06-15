import pygame
import pygame.freetype
from scripts.entities.player import Player


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        pygame.display.set_caption('Mario Pygame')
        self.screen = pygame.display.set_mode([1000, 800])
        self.font = pygame.freetype.SysFont("roboto", 24)

        self.active_sprite_list = pygame.sprite.Group()

        self.clock = pygame.time.Clock()
        self.player = Player()
        self.active_sprite_list.add(self.player)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        dt = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.active_sprite_list.update()
            self.active_sprite_list.draw(self.screen)

            self.font.render_to(self.screen, [20, 20], "Mario Pygame", (255, 255, 255))

            pygame.display.update()

            dt = clock.tick(60) / 1000


Game().run()