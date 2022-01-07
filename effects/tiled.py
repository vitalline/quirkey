from typing import Optional

from PIL import Image, ImageOps

from keyboard import manager

tiles = []
rotations = []
row, col = 0, 0
rows, cols = 0, 0
size = manager.char_size
empty_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
directions = {
    'u': (-1, 0),
    'd': (1, 0),
    'l': (0, -1),
    'r': (0, 1),
}
angles = {
    'cc': 90,
    'flip': 180,
    'cw': 270,
}
tile_map = None


def expand():
    global tiles, rotations, row, col, rows, cols, tile_map
    box = [tile_map.width, tile_map.height]
    position = [0, 0]
    while col < 0:
        tiles = [[None] + i for i in tiles]
        rotations = [[0] + i for i in rotations]
        col += 1
        cols += 1
        box[0] += size
        position[0] = 1
    while row < 0:
        tiles = [[None] * cols] + tiles
        rotations = [[0] * cols] + rotations
        row += 1
        rows += 1
        box[1] += size
        position[1] = 1
    while col >= cols:
        tiles = [r + [None] for r in tiles]
        rotations = [i + [0] for i in rotations]
        cols += 1
        box[0] += size
    while row >= rows:
        tiles = tiles + [[None] * cols]
        rotations = rotations + [[0] * cols]
        rows += 1
        box[1] += size
    tile_map = ImageOps.pad(tile_map, tuple(box), centering=tuple(position))


def shrink():
    global tiles, rotations, row, col, rows, cols, tile_map
    box = [0, 0, tile_map.width, tile_map.height]
    while col > 0 and tuple(tiles[i][0] for i in range(rows)) == (None,) * rows:
        tiles = [tiles[i][1:] for i in range(rows)]
        rotations = [rotations[i][1:] for i in range(rows)]
        col -= 1
        cols -= 1
        box[0] += size
    while row > 0 and tuple(tiles[0][i] for i in range(cols)) == (None,) * cols:
        tiles = tiles[1:]
        rotations = rotations[1:]
        row -= 1
        rows -= 1
        box[1] += size
    while cols > col + 1 and tuple(tiles[i][-1] for i in range(rows)) == (None,) * rows:
        tiles = [tiles[i][:-1] for i in range(rows)]
        rotations = [rotations[i][:-1] for i in range(rows)]
        cols -= 1
        box[2] -= size
    while rows > row + 1 and tuple(tiles[-1][i] for i in range(cols)) == (None,) * cols:
        tiles = tiles[:-1]
        rotations = rotations[:-1]
        rows -= 1
        box[3] -= size
    if box == [0, 0, 0, 0]:
        tile_map = None
    else:
        tile_map = tile_map.crop(tuple(box))


def process(_: Optional[Image.Image]) -> Optional[Image.Image]:
    global tiles, rotations, row, col, rows, cols, tile_map
    keyboard = manager.keyboard
    key = keyboard.current_key
    if not keyboard.current_key_is_pressed:
        return tile_map
    tile = key.base_image
    if rows > 0 and cols > 0:
        if key.name.startswith('dir_'):
            for direction, (delta_row, delta_col) in directions.items():
                if key.name.endswith(f'_{direction}'):
                    row += delta_row
                    col += delta_col
            expand()
        shrink()
        manager.next_key_position = [col * size, row * size]
        if key.name == 'clear':
            tiles[row][col] = None
            tile_map.paste(empty_image, tuple(manager.next_key_position))
            shrink()
        else:
            if key.name.startswith('rotate_'):
                if tiles[row][col] is not None:
                    for rotation, angle in angles.items():
                        if key.name.endswith(f'_{rotation}'):
                            rotations[row][col] = (rotations[row][col] + angle) % 360
            elif not key.name.startswith('dir_'):
                tiles[row][col] = tile
                rotations[row][col] = 0
            if tiles[row][col] is not None:
                tile = tiles[row][col].resize((size, size)).rotate(rotations[row][col])
                tile_map.paste(tile, tuple(manager.next_key_position))
    elif not (key.name.startswith('dir_') or key.name.startswith('rotate_') or key.name == 'clear'):
        tiles = [[tile]]
        rotations = [[0]]
        rows, cols = 1, 1
        manager.next_key_position = [0, 0]
        tile_map = tile.resize((size, size))
    return tile_map
