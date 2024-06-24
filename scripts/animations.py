import json
import os
from enum import Enum


class Image:
    def __init__(self, sheet_name, x, y):
        self.sheet_name = sheet_name
        self.x = x
        self.y = y

class Frame:
    def __init__(self, image, duration):
        self.image = image
        self.duration: int = duration
        
class AnimationDirection(Enum):
    NORMAL = 0
    FORWARD = 1
    BACKWARD = 2
    ALTERNATE = 3
    ALTERNATE_REVERSE = 4

class Animation:
    def __init__(self, frames: [], direction):
        self._frames = frames
        self._current_frame = 0
        self._start_dt = 0
        if isinstance(direction, int):
            direction = AnimationDirection(direction)

        self._direction = direction
        self._alternate_last_direction = AnimationDirection.FORWARD

        if self._direction == AnimationDirection.BACKWARD:
            self._current_frame = len(self._frames) - 1
            
        if self._direction == AnimationDirection.ALTERNATE_REVERSE:
            self._current_frame = len(self._frames) - 1
            self._alternate_last_direction = AnimationDirection.BACKWARD
            self._direction = AnimationDirection.ALTERNATE

    def get_current_frame(self, dt, speed=1):
        if self._start_dt == 0:
            self._start_dt = dt

        dt_change = dt - self._start_dt

        match self._direction:
            case AnimationDirection.NORMAL:
                if dt_change * speed >= self._frames[self._current_frame].duration:
                    if self._current_frame >= len(self._frames) - 1:
                        self._current_frame = 0
                        self._start_dt = 0
                    else:
                        self._current_frame += 1
                        self._start_dt = 0


            case AnimationDirection.FORWARD:
                if (dt_change * speed >= self._frames[self._current_frame].duration
                        and not self._current_frame >= len(self._frames) - 1):
                    self._current_frame += 1
                    self._start_dt = 0

            case AnimationDirection.BACKWARD:
                if (dt_change * speed >= self._frames[self._current_frame].duration
                        and not self._current_frame <= 0):
                    self._current_frame -= 1
                    self._start_dt = 0

            case AnimationDirection.ALTERNATE:
                if self._alternate_last_direction == AnimationDirection.FORWARD:
                    if dt_change * speed >= self._frames[self._current_frame].duration:
                        self._current_frame += 1
                        self._start_dt = 0

                    if self._current_frame >= len(self._frames) - 1:
                        self._alternate_last_direction = AnimationDirection.BACKWARD

                else:
                    if dt_change * speed >= self._frames[self._current_frame].duration:
                        self._current_frame -= 1
                        self._start_dt = 0

                    if self._current_frame <= 0:
                        self._alternate_last_direction = AnimationDirection.FORWARD

        return self._frames[self._current_frame]

class Animatable:
    def __init__(self, path):
        self._animatable_path = path
        self._animations = {}
        self._current_animation: Animation | None = None


    def get_path(self):
        return self._animatable_path


    def open(self, path=None):
        if path is not None:
            self._animatable_path = path

        if not os.path.exists(self._animatable_path):
            print(f"File {self._animatable_path} does not exist")
            return
        with open(self._animatable_path, 'r') as f:
            print(f'Opening {self._animatable_path}')
            f.seek(0)

            try:
                data = json.load(f)
            except:
                data = {}

            if not data:
                print("Empty")
                f.close()
                return

            self._current_animation = None
            for name, animation in data["animations"].items():
                frames = []

                for frame in animation["frames"]:
                    frames.append(Frame(Image(frame["image"]["sheet_name"], frame["image"]["x"], frame["image"]["y"]), frame["duration"]))

                animation = Animation(frames, animation["direction"])
                self.add_animation(name, animation)
                if self._current_animation is None:
                    self._current_animation = animation


            print(f"Loaded animation")
            print(f"Animation count: {len(self._animations)}")
            f.close()

    def add_animation(self, name, animation):
        self._animations[name] = animation

    def get_current_frame(self, dt) -> Frame:
        return self._current_animation.get_current_frame(dt)
    
    def set_animation(self, name):
        self._current_animation = self._animations[name]