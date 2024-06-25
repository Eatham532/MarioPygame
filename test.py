import os

import pygame

def test_load_tilesheet():
    directory = "./assets/tilesheets"
    files = os.listdir(directory)
    tilesheets = {}
    for file in files:
        if file.endswith(".png"):
            path = os.path.join(directory, file)
            tilesheets[file.strip(".png")] = pygame.image.load(path)

    print(tilesheets)


def test_create_dummy_class():
    from scripts.tilemap import TileMap
    from scripts.entities.special_tiles import question_block
    from scripts.entities.enemies import paragoomba

    tilemap = TileMap(None)
    dummy = question_block.QuestionBlock(tilemap, 0, 0, tilemap.scale, "normal")
    print(dummy)

    dummy = paragoomba.Paragoomba(tilemap, 0, 0, tilemap.scale)
    print(dummy)