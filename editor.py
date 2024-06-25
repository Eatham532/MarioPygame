import importlib
import os

import pygame
import pygame.freetype
import json
import datetime
import scripts
import scripts.entities.special_tiles
from scripts.utils.class_management import get_animatable_class_info, get_special_tile_class, get_special_tile_dummy_class, get_enemy_dummy_class, get_enemy_class

available_props = ["solid", "boing", "background", "hazard", "water"]
tilesheet_modes = ["tiles", "special", "enemies"]

class Tile(pygame.sprite.Sprite):
    def __init__(self, tilemap, x, y, scale, p, sheet_image, sheet_name, sheet_location=None, id=0, tilesheet_mode=0, tags=[]):
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

        self.tilesheet_mode = tilesheet_mode


        self.tags = tags

        self.has_init = False

        for sprite in tilemap.tiles:
            if sprite.x == x and sprite.y == y and not self.cursor and not sprite.cursor and sprite.id != self.id:
                sprite.kill()

    def update(self):
        self.offset = self.tilemap.offset
        self.rect.x = (self.x * self.size) + self.offset
        self.rect.y = (self.y * self.size)

        if self.rect.x < -self.rect.width or self.rect.x > self.tilemap.window_width + self.rect.width:
            return

        tile_size = 16

        self.image.fill((0, 0, 0))

        if self.tilemap.property_mode:
            match self.property:
                case "solid":
                    self.image.fill((0, 255, 0))
                case "boing":
                    self.image.fill((255, 255, 0))
                case "background":
                    self.image.fill((170, 50, 180))
                case "hazard":
                    self.image.fill((255, 0, 0))
                case "water":
                    self.image.fill((0, 0, 255))

        else:
            if self.cursor and self.tilemap.erase_mode:
                pass
            else:
                self.image.blit(self.sheet_image, (0, 0), (self.sheet_location[0] * tile_size * self.scale,
                                                           self.sheet_location[1] * tile_size * self.scale, self.size,
                                                           self.size))

        if self.tilesheet_mode == 1 and not (self.tilemap.erase_mode and self.cursor):
            self.tilemap.game.font.render_to(self.image, (0, 0), "S", (255, 255, 255))

        elif self.tilesheet_mode == 2 and not (self.tilemap.erase_mode and self.cursor):
            self.tilemap.game.font.render_to(self.image, (0, 0), "E", (255, 255, 255))

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
        self.game = game

        # Window stuff
        self.scale = 3
        self.window_height = self.game.screen.get_height()
        self.window_width = self.game.screen.get_width()
        self.world_height = round(self.window_height / (self.tile_size * self.scale))
        self.world_width = round(self.window_width / (self.tile_size * self.scale))
        self.world_name = name
        self.offset = 0

        self.tiles = pygame.sprite.Group()  # A group to hold all the tiles
        self.cursor = None  # A variable to hold the cursor sprite for positioning

        '''
        Load all the tilesheets
        '''
        files = os.listdir(tilesheets_path)
        self.tilesheets = {}
        for file in files:
            if file.endswith(".png"):
                path = os.path.join(tilesheets_path, file)
                image = pygame.image.load(path)
                scaled_image = pygame.transform.scale_by(image, self.scale)
                self.tilesheets[file.strip(".png")] = scaled_image

            elif file.endswith(".bmp"):
                path = os.path.join(tilesheets_path, file)
                image = pygame.image.load(path)
                scaled_image = pygame.transform.scale_by(image, self.scale)
                self.tilesheets[file.strip(".bmp")] = scaled_image

        '''
        Locate all the special tile class files
        '''
        self.special_tiles: {{}} = {}
        self.selected_special_tile = 0
        files = os.listdir("./scripts/entities/special_tiles")
        for file in files:
            if file.endswith(".py"):
                info = get_special_tile_dummy_class(self, file)
                if isinstance(info, scripts.animations.Animatable):
                    _file = open(info.get_path(), "r")
                    j = json.load(_file)
                    animation_info_group = j["animations"]
                    animation_info = animation_info_group[list(animation_info_group.keys())[0]]["frames"][0]["image"]

                    self.special_tiles[file.strip(".json")] = {
                        "name": file,
                        "sheet_image": self.tilesheets[animation_info["sheet_name"]],
                        "sheet_name": animation_info["sheet_name"],
                        "x": animation_info["x"],
                        "y": animation_info["y"],
                    }
                elif isinstance(info, scripts.entities.tile.Tile):
                    self.special_tiles[file.strip(".json")] = {
                        "name": file,
                        "sheet_image": self.tilesheets[info.sheet_name],
                        "sheet_name": info.sheet_name,
                        "x": info.sheet_location[0],
                        "y": info.sheet_location[1],
                    }

        '''
        Locate all the enemy class files
        '''
        self.enemies_group: {{}} = {}
        self.selected_enemy_index = 0
        files = os.listdir("./scripts/entities/enemies")
        for file in files:
            if file.endswith(".py"):
                info = get_enemy_dummy_class(self, file)
                if isinstance(info, scripts.entities.enemy.Enemy) and isinstance(info, scripts.animations.Animatable):
                    _file = open(info.get_path(), "r")
                    j = json.load(_file)
                    animation_info_group = j["animations"]
                    animation_info = animation_info_group[list(animation_info_group.keys())[0]]["frames"][0]["image"]

                    self.enemies_group[file.strip(".json")] = {
                        "name": file,
                        "sheet_image": self.tilesheets[animation_info["sheet_name"]],
                        "sheet_name": animation_info["sheet_name"],
                        "x": animation_info["x"],
                        "y": animation_info["y"],
                    }

        # The different modes
        self.erase_mode = False
        self.property_mode = False
        self.chosen_property_index = 0
        self.tilesheet_mode = 0

        # Selected variables
        self.selected_sheet = list(self.tilesheets.keys())[0]
        self.selected_tile = [0, 0]
        self.selected_sheet_index = 0

        self._tile_id = 0  # Tile id is used to check collisions
        self.last_saved = None  # The last time the world was saved

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
            world.append({"x": tile.x, "y": tile.y, "props": tile.property, "sheet_name": tile.sheet_name,
                          "sheet_pos": tile.sheet_location, "tile_type": tilesheet_modes[tile.tilesheet_mode]})

        data["world"] = world

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
                match tile["tile_type"]:
                    case "tile":
                        self.tiles.add(
                            Tile(self, tile["x"], tile["y"], self.scale, tile["props"],
                                 self.tilesheets[tile["sheet_name"]],
                                 tile["sheet_name"], tile["sheet_pos"], self._tile_id))
                    case "special_tile":
                        mod = self.special_tiles[tile["sheet_name"]]

                        self.tiles.add(
                            Tile(self, tile["x"], tile["y"], self.scale, available_props[self.chosen_property_index],
                                 mod["sheet_image"], mod["name"],
                                 [mod["x"], mod["y"]], -1, 1))
                    case "enemy":
                        self.tiles.add(
                            Tile(self, tile["x"], tile["y"], self.scale, tile["props"],
                                 self.tilesheets[tile["sheet_name"]],
                                 tile["sheet_name"], tile["sheet_pos"], self._tile_id, 2))

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
                        self.offset -= 0.5
                    else:
                        self.offset -= 0.1
                elif event.y < 0 or event.x < 0:  # Scroll Down
                    if shift:
                        self.offset += 0.5
                    else:
                        self.offset += 0.1


        self.game.event_check.append(detect_scroll)

        if key[pygame.K_LEFT]:
            self.offset -= self.tile_size / 2

        if key[pygame.K_RIGHT]:
            self.offset += self.tile_size / 2

        shift_press = key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]
        tile_shift = 1 if shift_press else 0
        self.selected_sheet = list(self.tilesheets.keys())[self.selected_sheet_index]

        '''
        Tile Shifting
        '''
        if not self.erase_mode:  # Only shift tiles if not erasing
            if mouse[1]:  # Middle mouse button
                for sprite in pygame.sprite.spritecollide(self.cursor, self.tiles, False):
                    if sprite.cursor or not isinstance(sprite, Tile):
                        continue

                    if not self.property_mode:
                        self.selected_tile = [sprite.sheet_location[0], sprite.sheet_location[1]]
                        if sprite.special_tile:
                            self.tilesheet_mode = 1
                        elif sprite.enemy:
                            self.tilesheet_mode = 2
                        else:
                            self.tilesheet_mode = 0

                        if self.tilesheet_mode:
                            self.selected_special_tile = list(self.special_tiles.keys()).index(sprite.sheet_name)

                    self.chosen_property_index = available_props.index(sprite.property)

            elif not self.property_mode and self.tilesheet_mode == 0:  # Shift normal tilesheet index
                if key_just[pygame.K_LEFTBRACKET]:
                    self.selected_tile[tile_shift] -= 1
                    if self.selected_tile[tile_shift] < 0:
                        self.selected_tile[tile_shift] = 0

                if key_just[pygame.K_RIGHTBRACKET]:
                    self.selected_tile[tile_shift] += 1

            elif self.property_mode:  # Shift property index
                if key_just[pygame.K_LEFTBRACKET]:
                    self.chosen_property_index -= 1
                    if self.chosen_property_index < 0:
                        self.chosen_property_index = len(available_props) - 1

                if key_just[pygame.K_RIGHTBRACKET]:
                    self.chosen_property_index += 1
                    if self.chosen_property_index >= len(available_props):
                        self.chosen_property_index = 0

            elif self.tilesheet_mode == 1:  # Shift special tile index
                if key_just[pygame.K_LEFTBRACKET]:
                    self.selected_special_tile -= 1
                    if self.selected_special_tile < 0:
                        self.selected_special_tile = len(self.special_tiles) - 1

                if key_just[pygame.K_RIGHTBRACKET]:
                    self.selected_special_tile += 1
                    if self.selected_special_tile >= len(self.special_tiles):
                        self.selected_special_tile = 0

            elif self.tilesheet_mode == 2:  # Shift enemy index
                if key_just[pygame.K_LEFTBRACKET]:
                    self.selected_enemy_index -= 1
                    if self.selected_enemy_index < 0:
                        self.selected_enemy_index = len(self.enemies_group) - 1

                if key_just[pygame.K_RIGHTBRACKET]:
                    self.selected_enemy_index += 1
                    if self.selected_enemy_index >= len(self.enemies_group):
                        self.selected_enemy_index = 0

            '''
            Shift tilesheet
            '''
            if not self.property_mode and self.tilesheet_mode == 0:
                if key_just[pygame.K_COMMA]:
                    self.selected_sheet_index -= 1
                    if self.selected_sheet_index < 0:
                        self.selected_sheet_index = len(self.tilesheets) - 1

                elif key_just[pygame.K_PERIOD]:
                    self.selected_sheet_index += 1
                    if self.selected_sheet_index >= len(self.tilesheets):
                        self.selected_sheet_index = 0

        '''
        Single key press events
        '''

        if key_just[pygame.K_s]:  # Save
            self.save(self.world_name)

        elif key_just[pygame.K_o]:  # Open
            name = input("Enter the name of the world: ")
            self.open(name)

        elif key_just[pygame.K_e]:  # Erase mode
            self.erase_mode = not self.erase_mode

        elif key_just[pygame.K_p]:  # Property mode
            self.property_mode = not self.property_mode

        elif key_just[pygame.K_t]:  # Tilesheet switch
            self.tilesheet_mode += 1
            if self.tilesheet_mode >= len(tilesheet_modes):
                self.tilesheet_mode = 0

        if self.game.screen.get_height() != self.window_height or self.game.screen.get_width() != self.window_width:
            self.window_height = self.game.screen.get_height()
            self.window_width = self.game.screen.get_width()
            self.world_height = round(self.window_height / (self.tile_size * self.scale))
            self.world_width = round(self.window_width / (self.tile_size * self.scale))

        '''
        Mouse down event
        '''
        if mouse[0] and not self.erase_mode and not self.property_mode:
            if self.tilesheet_mode == 1:
                mod = self.special_tiles[list(self.special_tiles.keys())[self.selected_special_tile]]

                self.tiles.add(Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                                    mod["sheet_image"], mod["name"],
                                    [mod["x"], mod["y"]], self._tile_id,1))

            elif self.tilesheet_mode == 2:
                mod = self.enemies_group[list(self.enemies_group.keys())[self.selected_enemy_index]]

                self.tiles.add(Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                                    mod["sheet_image"], mod["name"],
                                    [mod["x"], mod["y"]], self._tile_id, 2))

            else:
                self.tiles.add(Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                                    self.tilesheets[self.selected_sheet],
                                    self.selected_sheet, self.selected_tile, self._tile_id))
            self._tile_id += 1

        '''
        Create the cursor
        '''
        if self.tilesheet_mode == 1:
            mod = self.special_tiles[list(self.special_tiles.keys())[self.selected_special_tile]]

            tile_cursor = Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                               mod["sheet_image"], mod["name"],
                               [mod["x"], mod["y"]], -1, 1, ["cursor"])
            tile_cursor.update()
            self.cursor = tile_cursor

        elif self.tilesheet_mode == 2:
            mod = self.enemies_group[list(self.enemies_group.keys())[self.selected_enemy_index]]

            tile_cursor = Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                               mod["sheet_image"], mod["name"],
                               [mod["x"], mod["y"]], -1, 2, ["cursor"])
            tile_cursor.update()
            self.cursor = tile_cursor

        else:
            tile_cursor = Tile(self, x, y, self.scale, available_props[self.chosen_property_index],
                               self.tilesheets[self.selected_sheet], self.selected_sheet,
                               self.selected_tile, -1, tags=["cursor"])
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

        match self.tilesheet_mode:
            case 1:
                self.game.font.render_to(screen, (10, 70), f"Special Tiles Mode. Using: {list(self.special_tiles.keys())[self.selected_special_tile]}", (100, 150, 200))
            case 2:
                self.game.font.render_to(screen, (10, 70), f"Enemy Mode. Using: {list(self.enemies_group.keys())[self.selected_enemy_index]}", (150, 150, 150))
            case _:
                self.game.font.render_to(screen, (10, 70),
                                 f"Normal Mode: {list(self.tilesheets.keys())[self.selected_sheet_index]}",
                                 (218,112,214))

        if self.last_saved:
            text = f"Last saved {self.last_saved}"
            text_surface, text_rect = self.game.font.render(text, (0, 0, 0))
            x_position = self.game.screen.get_width() - text_rect.width - 10
            self.game.font.render_to(screen, (x_position, 10), text, (255, 255, 255))


class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Editor')
        self.screen = pygame.display.set_mode([1000, 800])
        self.font = pygame.freetype.SysFont("roboto", 24)
        self.dt = 0
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
            self.dt += clock.tick(60)


Editor().run()
