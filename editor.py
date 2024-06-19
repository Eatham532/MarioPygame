import os

import pygame
import pygame.freetype
import json
import datetime

from scripts.utils.color import hsl_to_rgb

available_props = ["solid", "background", "hazard", "water"]

class Tile(pygame.sprite.Sprite):
    def __init__(self, tilemap, x, y, scale, p, sheet_image, sheet_name, sheet_location=None, id=0, tags=[]):
        super().__init__()

        self.tilemap = tilemap
        self.scale = scale
        self.size = tilemap.tile_size * self.scale
        self.image = pygame.Surface([self.size, self.size])
        self.property = p

        self.rect = self.image.get_rect()
        self.offset = tilemap.offset
        self.x = x
        self.y = y

        self.id = id

        if sheet_location is None:
            sheet_location = [0, 0]
        else: sheet_location = [sheet_location[0], sheet_location[1]]

        self.sheet_image = sheet_image
        self.sheet_location = sheet_location
        self.sheet_name = sheet_name

        self.cursor = "cursor" in tags
        if self.cursor:
            tags.remove("cursor")


        self.tags = tags

        self.has_init = False

        for sprite in tilemap.tiles:
            if sprite.x == x and sprite.y == y and not self.cursor and not sprite.cursor and sprite.id != self.id:
                sprite.kill()



    def update(self):
        self.offset = self.tilemap.offset
        self.rect.x = (self.x * self.size) + self.offset
        self.rect.y = (self.y * self.size)

        tile_size = 16

        self.image.fill((0, 0, 0))

        if self.tilemap.property_mode:
            match self.property:
                case "solid":
                    self.image.fill((0, 255, 0))
                case "background":
                    self.image.fill((170, 50, 180))
                case "hazard":
                    self.image.fill((255, 0, 0))
                case "water":
                    self.image.fill((0, 0, 255))

        else:
            self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * tile_size * self.scale,
                                                       self.sheet_location[1] * tile_size * self.scale, self.size, self.size))

        pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        if mouse[0] and not self.cursor and self.has_init:
            if self.rect.collidepoint(pos):
                if self.tilemap.property_mode:
                    self.property = available_props[self.tilemap.chosen_property_index]
                else:
                    self.kill()

        if not mouse[0] and not self.has_init:
            self.has_init = True



class EditorTileMap:
    def __init__(self, game, tile_size=16, name="world", tilesheets_path="./assets/tilesheets/"):
        self.tile_size = tile_size
        self.offset = 0
        self.game = game

        self.scale = 3
        self.window_height = self.game.screen.get_height()
        self.window_width = self.game.screen.get_width()
        self.world_height = round(self.window_height / (self.tile_size * self.scale))
        self.world_width = round(self.window_width / (self.tile_size * self.scale))
        self.world_name = name

        self.tiles = pygame.sprite.Group()
        self.cursor = None

        files = os.listdir(tilesheets_path)
        self.tilesheets = {}
        for file in files:
            if file.endswith(".png"):
                path = os.path.join(tilesheets_path, file)
                image = pygame.image.load(path)
                scaled_image = pygame.transform.scale_by(image, self.scale)
                self.tilesheets[file.strip(".png")] = scaled_image

        self.selected_sheet = list(self.tilesheets.keys())[0]
        self.selected_tile = [0, 0]

        self.erase_mode = False
        self.property_mode = False
        self.last_saved = None

        self._tile_id = 0
        self.chosen_property_index = 0

        self.open(name)

    def save(self, name):
        os.makedirs(f'./assets/worlds/', exist_ok=True)
        f = open(f'./assets/worlds/{name}.json', 'w')
        try:
            data = json.load(f)
        except:
            data = {}

        data["tile_size"] = self.tile_size

        world = []

        for tile in self.tiles:
            world.append({"x": tile.x, "y": tile.y, "props": tile.property,"sheet_name": tile.sheet_name, "sheet_pos": tile.sheet_location})

        data["world"] = world

        print(data)
        self.last_saved = datetime.datetime.now().strftime("%H:%M:%S")
        json.dump([data], f)
        f.close()

    def open(self, name):
        with open(f'./assets/worlds/{name}.json', 'a+') as f:
            print(f'./assets/worlds/{name}.json')
            f.seek(0)

            try:
                data = json.load(f)[0]
            except:
                data = {}

            if not data:
                print("Empty")
                self.world_name = name
                self.tiles.empty()
                f.close()
                return

            self.tile_size = data["tile_size"]

            self.tiles.empty()

            for tile in data["world"]:
                self.tiles.add(Tile(self, tile["x"], tile["y"], self.scale, tile["props"], self.tilesheets[tile["sheet_name"]], tile["sheet_name"], tile["sheet_pos"], self._tile_id))
                self._tile_id += 1

            print(f"Loaded world: {name}")
            print(f"Tile count: {len(self.tiles)}")
            self.world_name = name
            f.close()

    def update(self):
        key = pygame.key.get_pressed()
        key_just = pygame.key.get_just_pressed()
        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        x = (pos[0] - self.offset) // (self.tile_size * self.scale)
        y = pos[1] // (self.tile_size * self.scale)

        def detect_scroll(event, mouse_pos):
            k = pygame.key.get_pressed()
            shift = k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0 or event.x > 0:  # Scroll Up
                    if shift:
                        self.offset -= 1
                    else:
                        self.offset -= 0.2
                elif event.y < 0 or event.x < 0:  # Scroll Down
                    if shift:
                        self.offset += 1
                    else:
                        self.offset += 0.2


        self.game.event_check.append(detect_scroll)

        if self.erase_mode:
            pass

        if key[pygame.K_LEFT]:
            self.offset -= self.tile_size / 2

        if key[pygame.K_RIGHT]:
            self.offset += self.tile_size / 2

        shift_press = key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]
        tile_shift = 0
        if shift_press:
            tile_shift = 1

        if not self.property_mode or not self.erase_mode:
            if key_just[pygame.K_LEFTBRACKET]:
                self.selected_tile[tile_shift] -= 1
                if self.selected_tile[tile_shift] < 0:
                    self.selected_tile[tile_shift] = 0

            if key_just[pygame.K_RIGHTBRACKET]:
                self.selected_tile[tile_shift] += 1

            if mouse[1]:
                for sprite in pygame.sprite.spritecollide(self.cursor, self.tiles, False):
                    if sprite.cursor or not isinstance(sprite, Tile):
                        continue
                    self.selected_tile = [sprite.sheet_location[0], sprite.sheet_location[1]]
                    self.chosen_property_index = available_props.index(sprite.property)

        if self.property_mode:
            if key_just[pygame.K_LEFTBRACKET]:
                self.chosen_property_index -= 1
                if self.chosen_property_index < 0:
                    self.chosen_property_index = len(available_props) - 1

            if key_just[pygame.K_RIGHTBRACKET]:
                self.chosen_property_index += 1
                if self.chosen_property_index >= len(available_props):
                    self.chosen_property_index = 0

        if key_just[pygame.K_s]:
            self.save(self.world_name)

        if key_just[pygame.K_o]:
            name = input("Enter the name of the world: ")
            self.open(name)

        if key_just[pygame.K_e]:
            self.erase_mode = not self.erase_mode

        if key_just[pygame.K_p]:
            self.property_mode = not self.property_mode

        if self.game.screen.get_height() != self.window_height or self.game.screen.get_width() != self.window_width:
            self.window_height = self.game.screen.get_height()
            self.window_width = self.game.screen.get_width()
            self.world_height = round(self.window_height / (self.tile_size * self.scale))
            self.world_width = round(self.window_width / (self.tile_size * self.scale))


        if mouse[0] and not self.erase_mode and not self.property_mode:
            self.tiles.add(Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                                self.tilesheets[self.selected_sheet],
                                self.selected_sheet, self.selected_tile, self._tile_id))
            self._tile_id += 1

        tile_cursor = Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                           self.tilesheets[self.selected_sheet], self.selected_sheet,
                           self.selected_tile, -1, ["cursor"])
        tile_cursor.update()
        self.cursor = tile_cursor

        self.tiles.update()

    def render(self, screen: pygame.Surface):
        self.tiles.draw(screen)
        self.game.screen.blit(self.cursor.image, [self.cursor.rect.x, self.cursor.rect.y])
        self.game.font.render_to(screen, (10, 10), f"World File: {self.world_name}.json     Selected Property: {available_props[self.chosen_property_index]}", (255, 255, 255))

        if self.erase_mode:
            self.game.font.render_to(screen, (10, 40), f"ERASE", (255, 0, 0))

        if self.property_mode:
            self.game.font.render_to(screen, (90, 40), f"Property Mode", (0, 200, 0))

        if self.last_saved:
            text = f"Last saved {self.last_saved}"
            text_surface, text_rect = self.game.font.render(text, (0, 0, 0))
            x_position = self.game.screen.get_width() - text_rect.width - 10
            self.game.font.render_to(screen, (x_position, 10), text, (255, 255, 255))


class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1000, 800])
        self.font = pygame.freetype.SysFont("roboto", 24)
        self.dt = None
        self.event_check = []

        self.tile_map = EditorTileMap(self)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        self.dt = 0

        while running:
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    running = False

                for e in self.event_check:
                    e(event, mouse_pos)

            self.screen.fill((0, 0, 0))

            self.tile_map.update()
            self.tile_map.render(self.screen)

            pygame.display.update()
            self.dt = clock.tick(60) / 1000


Editor().run()
