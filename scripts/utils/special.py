import importlib
import json

from scripts.animations import Animatable

def get_special_tile_dummy_class(tilemap, file):
    info = get_special_tile_class(file)

    return info(tilemap, 0, 0, tilemap.scale, "normal")

def get_animatable_class_info(tilemap, file):
    tile: Animatable = get_special_tile_dummy_class(tilemap, file)
    j = open(tile.get_path(), "r")

    return json.load(j)

def get_special_tile_class(file):
    module_name = f'./special_tiles/{file}'.replace('/', '.').rstrip('.py')
    mod_name = [e.capitalize() for e in file.strip(".py").split("_")]
    mod_name = "".join(mod_name)
    info = importlib.import_module(module_name, package="scripts.entities.special_tiles")
    info = getattr(info, mod_name)

    return info