import importlib
import json


def get_special_tile_info(tilemap, file):
    info = get_special_tile_class(file)

    tile = info(tilemap, 0, 0, tilemap.scale, "normal")

    j = open(tile._animatable_path, "r")

    return json.load(j)

def get_special_tile_class(file):
    module_name = f'./special_tiles/{file}'.replace('/', '.').rstrip('.py')
    mod_name = [e.capitalize() for e in file.strip(".py").split("_")]
    mod_name = "".join(mod_name)
    info = importlib.import_module(module_name, package="scripts.entities.special_tiles")
    info = getattr(info, mod_name)

    return info