import os

import pygame

directory = "./assets/tilesheets"
files = os.listdir(directory)
tilesheets = {}
for file in files:
    if file.endswith(".png"):
        path = os.path.join(directory, file)
        tilesheets[file.strip(".png")] = pygame.image.load(path)

print(tilesheets)