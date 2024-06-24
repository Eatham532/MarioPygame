# Mario Pygame

A recreation of the classic Mario game using Pygame. 

## Running

1. Ensure you have Python 3.8 or later installed.
2. Install `pygame-ce` using pip
3. Run `game.py` to play and `editor.py` to create levels.

## Controls
### Game Editor
- `Left Click` to place a cube
- `E` to enable erase mode. Use `Left Click` to erase cubes
- `P` to enable property mode. Use `Left Click` to change the properties of a tile
- `T` to access special tiles. `[` and `]` to cycle through the special tiles
- `S` to save the level
- `O` to open a level. Use the python terminal to input the level name
- `[` to move left along the tile sheet
- `]` to move right along the tile sheet
- `[` + `shift` to move up along the tile sheet
- `]` + `shift` to move down along the tile sheet
- `scroll` or `left` and `right` to move around. `shift` to move faster
- `middle click` to set the current tile and property to that of the tile

### Animation Editor
- `S` to save the animation
- `P` to play the animation
- `O` to open an animation set. Use the python terminal to input the file name
- `N` to add a frame
- `BACKSPACE` to delete the current frame
- `[` to move left along the tile sheet
- `]` to move right along the tile sheet
- `[` + `shift` to move up along the tile sheet
- `]` + `shift` to move down along the tile sheet
- `9` to cycle animation mode back
- `0` to cycle animation mode forward

### Game
- `Left` to move left
- `Right` to move right
- `Space` to jump