import os
import time
from enum import Enum

import pygame
import pygame.freetype

from scripts.tilemap import TileMap
from scripts.entities.player import Player

version = "Beta 0.0.1"

class GameState(Enum):
    HOME = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

def GetFont(size: int):
    return pygame.freetype.SysFont("roboto", size)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Create the window
        pygame.display.set_caption('Mario Pygame')
        self.screen = pygame.display.set_mode([1000, 800])
        self.font = {
            "small": GetFont(16),
            "medium": GetFont(24),
            "large": GetFont(36),
        }

        audio_files = os.listdir('./assets/audio')

        # Create a dictionary to store the audio files
        self.audio = {}

        # Load each audio file
        for file in audio_files:
            # Get the file name without the extension
            name = os.path.splitext(file)[0]
            # Load the audio file and store it in the dictionary
            self.audio[name] = pygame.mixer.Sound(f'./assets/audio/{file}')


        self.active_sprite_list = pygame.sprite.Group()
        self.player_dead = False

        self.clock = pygame.time.Clock()
        self.music_playing = False
        self.audio_mute = False
        self.coins = 0

        self.tile_map = TileMap(self)

        self.world_name = "world"
        self.game_state = GameState.HOME

        self.dt = 0
        # A variable to check to prevent the player from accidentally starting a new game
        self.game_over_dt = None


    def kill_player(self):
        self.player_dead = True

    def set_game_state(self, state: int):
        match state:
            case 0: self.game_state = GameState.HOME
            case 1: self.game_state = GameState.PLAYING
            case 2: self.game_state = GameState.PAUSED
            case 3: self.game_state = GameState.GAME_OVER


    def run(self):
        running = True
        clock = pygame.time.Clock()

        pygame.mixer.music.load('./assets/music/ground_theme.mp3')

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((0, 0, 0))

            if self.game_state == GameState.HOME:
                self.font["medium"].render_to(self.screen, (10, 10), f"Press SPACE to start", (255, 255, 255))
                self.font["medium"].render_to(self.screen, (10, 40), f"Press Q to quit", (255, 255, 255))
                self.font["small"].render_to(self.screen,
                                             [10, self.screen.get_height() - 24],
                                             f"Credits: Eatham532", (255, 255, 255))
                keys = pygame.key.get_just_pressed()
                if keys[pygame.K_SPACE]:
                    self.game_state = GameState.PLAYING
                    self.tile_map.open(self.world_name)
                    self.player_dead = False
                    self.coins = 0

                if keys[pygame.K_q]:
                    running = False

            elif self.game_state == GameState.PLAYING:
                if not self.music_playing:
                    pygame.mixer.stop()
                    pygame.mixer.music.play()
                    self.music_playing = True
                    self.game_over_dt = None

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()

                self.active_sprite_list.update()
                self.tile_map.update()

            if pygame.key.get_just_pressed()[pygame.K_m]:
                self.audio_mute = not self.audio_mute
                if self.audio_mute:
                    pygame.mixer.music.set_volume(0)
                else:
                    pygame.mixer.music.set_volume(100)

            if self.game_state == GameState.PLAYING or self.game_state == GameState.PAUSED:
                self.tile_map.render(self.screen)
                self.active_sprite_list.draw(self.screen)
                self.font["medium"].render_to(self.screen, [20, 20], f"Mario Pygame {version}", (255, 255, 255))
                self.font["small"].render_to(self.screen, [20, 50], f"World name: {self.tile_map.world_name}", (255, 255, 255))
                self.font["medium"].render_to(self.screen, [self.screen.get_width() - 100, 20], f"FPS: {round(clock.get_fps())}", (255, 255, 255))
                self.font["small"].render_to(self.screen, [20, 80], f"Coins: {self.coins}", (255, 255, 255))

            if self.game_state == GameState.GAME_OVER:
                if self.music_playing:
                    pygame.mixer.music.stop()
                    self.play_effect("smb_gameover")
                    self.music_playing = False

                self.font["large"].render_to(self.screen, [10, 10], f"Game Over", (255, 0, 0))
                self.font["medium"].render_to(self.screen, [10, 40], f"Press SPACE to restart", (255, 255, 255))
                self.font["medium"].render_to(self.screen, [10, 70], f"Press Q to quit", (255, 255, 255))
                self.font["small"].render_to(self.screen,
                                             [10, self.screen.get_height() - 24],
                                             f"Credits: Eatham532", (255, 255, 255))

                if self.game_over_dt is None:
                    self.game_over_dt = int(self.dt)

                if self.dt - self.game_over_dt >= 500:
                    keys = pygame.key.get_just_pressed()
                    if keys[pygame.K_SPACE]:
                        self.game_state = GameState.PLAYING
                        self.tile_map.open(self.world_name)
                        self.coins = 0

                    if keys[pygame.K_q]:
                        running = False

            pygame.display.update()

            self.dt += clock.tick(60)

    def play_effect(self, name: str):
        if not self.audio_mute:
            self.audio[name].play()


Game().run()
