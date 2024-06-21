import os
from datetime import datetime

import pygame
import pygame.freetype
from scripts.animations import *

'''
TODO: 

- Change animation mode
- Allow the ability to add multiple animations
- Chose animation save location
'''

animation_mode_options = ["Normal", "Forward", "Backward", "Alternate", "Alternate Reverse"]

class AnimationViewer(pygame.sprite.Sprite, Animatable):
    def __init__(self, posx, posy, scale, sheet):
        Animatable.__init__(self, "./animation.json")
        pygame.sprite.Sprite.__init__(self)

        self.size = 16 * scale
        self.image = pygame.surface.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.set_colorkey((1, 1, 1))
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
        self.sheet = sheet
        self.show = False

        self.open()

    def update(self, dt):
        self.image.fill((1, 1, 1))
        if not self.show:
            return
        self.image.fill((0,0,0))
        frame = self.get_current_frame(dt)
        self.image.blit(self.sheet, (0, 0), (frame.image.x * self.size, frame.image.y * self.size, self.size, self.size))

    def reload(self):
        self.open("./animation.json")


class ViewerFrame(pygame.sprite.Sprite):
    def __init__(self, tilesheet, viewer, image: Image, scale=1):
        super().__init__()

        self.tile_size = 16

        self.image = pygame.surface.Surface([self.tile_size * scale, self.tile_size * scale], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 300
        self.scale = scale
        self.size = self.tile_size * scale

        self.sheet = tilesheet
        self.viewer = viewer

        self.i = image

    def update(self):
        self.image.fill((0, 0, 0))
        self.image.blit(self.sheet, (0, 0), (self.viewer.tilesheet_x * self.size,
                                             self.viewer.tilesheet_y * self.size, self.size, self.size))





class Viewer:
    def __init__(self, editor, tilesheet_name, scale=20):
        path = os.path.join("./assets/tilesheets", tilesheet_name)
        image = pygame.image.load(path)
        scaled_image = pygame.transform.scale_by(image, scale)
        self.tilesheet = scaled_image
        self.tilesheet_name = tilesheet_name
        self.scale = scale

        self.frames = []

        self.tilesheet_x = 0
        self.tilesheet_y = 0
        self.animation_mode = 0

        self.current_frame_id = 0
        self.frames.append(Frame(Image(self.tilesheet_name, self.tilesheet_x, self.tilesheet_x), 1000))
        self.current_frame_duration = self.frames[self.current_frame_id].duration

        self.animation_name = "animation"
        self.animation_set_name = "animation"
        self._animatable_path = "./animation.json"
        self.editor = editor
        self.last_saved = None

        self.load(f"./assets/animations/{self.animation_set_name}.json")

        self.viewerFrame = ViewerFrame(self.tilesheet, self, self.frames[self.current_frame_id].image, scale)
        self.viewerFrameGroup = pygame.sprite.GroupSingle(self.viewerFrame)

        self.preview = AnimationViewer(300, 300, 20, self.tilesheet)
        self.previewGroup = pygame.sprite.GroupSingle(self.preview)

    def update(self):
        key_just = pygame.key.get_just_pressed()
        key = pygame.key.get_pressed()
        shift_press = key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]

        tile_shift = 1 if shift_press else 0

        if tile_shift:
            if key_just[pygame.K_LEFTBRACKET]:
                self.tilesheet_y -= 1
                if self.tilesheet_y < 0:
                    self.tilesheet_y = 0

            if key_just[pygame.K_RIGHTBRACKET]:
                self.tilesheet_y += 1

        else:
            if key_just[pygame.K_LEFTBRACKET]:
                self.tilesheet_x -= 1
                if self.tilesheet_x < 0:
                    self.tilesheet_x = 0

            if key_just[pygame.K_RIGHTBRACKET]:
                self.tilesheet_x += 1

        if key_just[pygame.K_n]:
            self.current_frame_id += 1
            self.frames.insert(self.current_frame_id, Frame(Image(self.tilesheet_name, self.tilesheet_x, self.tilesheet_y), 1000))
            self.current_frame_duration = self.frames[self.current_frame_id].duration

        if key_just[pygame.K_RIGHT]:
            self.current_frame_id += 1
            if self.current_frame_id >= len(self.frames):
                self.current_frame_id = 0

            self.update_frame_info()

        if key_just[pygame.K_LEFT]:
            self.current_frame_id -= 1
            if self.current_frame_id < 0:
                self.current_frame_id = len(self.frames) - 1

            self.update_frame_info()


        if key_just[pygame.K_MINUS]:
            self.current_frame_duration -= 100

        elif key_just[pygame.K_EQUALS]:
            self.current_frame_duration += 100

        elif key_just[pygame.K_s]:
            self.save(f"./assets/animations/{self.animation_set_name}.json")

        elif key_just[pygame.K_o]:
            name = input("Enter the animation set name: ")
            self.animation_set_name = name
            self.load(f"./assets/animations/{self.animation_set_name}.json")

        elif key_just[pygame.K_BACKSPACE]:
            self.remove_current_frame()

        elif key_just[pygame.K_p]:
            self.save()
            self.preview.reload()
            self.preview.show = not self.preview.show

        elif key_just[pygame.K_0]:
            self.animation_mode += 1
            if self.animation_mode >= len(animation_mode_options):
                self.animation_mode = 0

        elif key_just[pygame.K_9]:
            self.animation_mode -= 1
            if self.animation_mode < 0:
                self.animation_mode = len(animation_mode_options) - 1


        self.frames[self.current_frame_id].duration = self.current_frame_duration
        self.frames[self.current_frame_id].image = Image(self.tilesheet_name, self.tilesheet_x, self.tilesheet_y)

        self.viewerFrameGroup.update()
        self.viewerFrameGroup.draw(self.editor.screen)

        self.previewGroup.update(self.editor.dt)
        self.previewGroup.draw(self.editor.screen)

        pass

    def save(self, path="./animation.json"):
        if not os.path.exists("./assets/animations"):
            os.mkdir("./assets/animations")
        dump = {"animations": {}}
        dump["animations"][self.animation_name] = {"frames": [], "direction": self.animation_mode}
        for frame in self.frames:
            dump["animations"][self.animation_name]["frames"].append({"image": {"sheet_name": frame.image.sheet_name, "x": frame.image.x, "y": frame.image.y}, "duration": frame.duration})

        with open(path, "w") as f:
            json.dump(dump, f)

        print("Saved")
        print(dump)

        if path != self._animatable_path:
            self.last_saved = datetime.now().strftime("%H:%M:%S")

    def load(self, path="./animation.json"):
        if not os.path.exists(path):
            self.clear()

            print(f"File {path} does not exist")
            return
        with open(path, "a+") as f:
            print(path)
            f.seek(0)

            self.frames = []
            data = json.load(f)
            self.animation_name = list(data["animations"].keys())[0]
            for frame in data["animations"][self.animation_name]["frames"]:
                self.frames.append(Frame(Image(frame["image"]["sheet_name"], frame["image"]["x"], frame["image"]["y"]),
                                         frame["duration"]))

        self.update_frame_info()


    def remove_current_frame(self):
        self.frames.pop(self.current_frame_id)
        if self.current_frame_id == 0:
            self.current_frame_id = 0
        else:
            self.current_frame_id -= 1

        self.update_frame_info()


    def update_frame_info(self):
        self.current_frame_duration = self.frames[self.current_frame_id].duration
        self.tilesheet_x = self.frames[self.current_frame_id].image.x
        self.tilesheet_y = self.frames[self.current_frame_id].image.y

    def clear(self):
        self.frames.clear()
        self.current_frame_id = 0
        self.tilesheet_x = 0
        self.tilesheet_y = 0
        self.frames.append(Frame(Image(self.tilesheet_name, self.tilesheet_x, self.tilesheet_x), 1000))

        self.update_frame_info()

    def render(self):
        self.editor.font.render_to(self.editor.screen, (10, 10), f"Frame Id: {self.current_frame_id}  Frame Count: {len(self.frames)}", (255, 255, 255))
        self.editor.font.render_to(self.editor.screen, (10, 40), f"Frame Duration: {self.current_frame_duration}",
                                   (255, 255, 255))
        self.editor.font.render_to(self.editor.screen, (10, 70), f"Current Animation Set: {self.animation_set_name}",
                                   (255, 255, 255))

        self.editor.font.render_to(self.editor.screen, (10, 100), f"Animation Name: {self.animation_name}",
                                   (255, 255, 255))

        if self.preview.show:
            self.editor.font.render_to(self.editor.screen, (10, 130), f"Running Animation",
                                       (0, 255, 0))

        if self.last_saved:
            text = f"Last saved {self.last_saved}"
            text_surface, text_rect = self.editor.font.render(text, (0, 0, 0))
            x_position = self.editor.screen.get_width() - text_rect.width - 10
            self.editor.font.render_to(self.editor.screen, (x_position, 10), text, (255, 255, 255))

        text = f"Animation Mode: {animation_mode_options[self.animation_mode]}"
        text_surface, text_rect = self.editor.font.render(text, (0, 0, 0))
        y_position = self.editor.screen.get_height() - text_rect.height - 10
        self.editor.font.render_to(self.editor.screen, (10, y_position), text, (255, 255, 255))




class AnimationEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1000, 800])
        pygame.display.set_caption('Animation Editor')

        self.font = pygame.freetype.SysFont("roboto", 24)
        self.dt = None
        self.event_check = []

        self.viewer = Viewer(self, "tiles.png")


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

            self.screen.fill((0,0,0))

            self.viewer.update()
            self.viewer.render()

            pygame.display.update()
            self.dt += clock.tick(60)

        os.remove(self.viewer._animatable_path)


AnimationEditor().run()
