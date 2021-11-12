import random
from io import BytesIO
from itertools import product
from random import sample
from typing import Tuple, Union

from cocos import scene
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.sprite import Sprite
from pyglet import image
from pyglet.window import key, mouse
from wand.image import Image


class Key(Sprite):
    def __init__(self, name: str = 'none', board: str = 'util'):
        super().__init__(f"assets/{board}/{name}.png")
        self.board = board
        self.name = name

    def get_path(self) -> str:
        return f"assets/{self.board}/{self.name}.png"

    def is_empty(self):
        return self.name == 'none'


class Keyboard(ColorLayer):

    def __init__(self):
        self.is_event_handler = True

        self.board_height = 5
        self.board_width = 12
        self.screen_height = 3
        self.cell_size = 64
        self.cell_spacing = 4
        self.cell_color_0 = 187, 119, 51
        self.cell_color_1 = 255, 204, 153
        self.highlight_color = 255, 255, 255
        self.highlight_opacity = 50
        self.key_press_color = 255, 221, 187
        self.key_press_scale = 1.25
        window_width = (self.board_width + 1) * (self.cell_size + self.cell_spacing)
        window_height = (self.board_height + self.screen_height + 1) * (self.cell_size + self.cell_spacing)
        director.init(width=window_width, height=window_height, autoscale=False)
        super().__init__(192, 168, 142, 1000)

        # super boring initialization stuff (bluh bluh)
        self.image_buffer = None
        self.clicked_key = None
        self.selected_key = None
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.highlight = Sprite("assets/util/cell.png", color=self.highlight_color, opacity=0)
        self.highlight.scale = self.cell_size / self.highlight.width
        self.selection = Sprite("assets/util/cell.png", color=self.key_press_color, opacity=0)
        self.selection.scale = self.cell_size / self.selection.width * self.key_press_scale
        self.keys = BatchNode()
        self.active_key = BatchNode()
        self.add(self.board, z=1)
        self.add(self.highlight, z=2)
        self.add(self.keys, z=3)
        self.add(self.active_key, z=3)
        self.active_key.add(self.selection)

        for row in range(self.board_height):
            self.board_sprites += [[]]
            self.key_sprites += [[]]

        for row, col in product(range(self.board_height), range(self.board_width)):

            self.board_sprites[row] += [Sprite("assets/util/cell.png")]
            self.board_sprites[row][col].position = self.get_position((row, col))
            self.board_sprites[row][col].scale = self.cell_size / self.board_sprites[row][col].width
            self.board_sprites[row][col].color = self.get_cell_color((row, col))
            self.board.add(self.board_sprites[row][col])

            self.key_sprites[row] += [Key('lower_' + chr(random.randint(ord('a'), ord('z'))), 'hs')]
            self.key_sprites[row][col].position = self.get_position((row, col))
            self.key_sprites[row][col].scale = self.cell_size / self.key_sprites[row][col].width
            self.keys.add(self.key_sprites[row][col])

        director.run(scene.Scene(self))

    def get_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        window_width, window_height = director.get_window_size()
        x, y = director.get_virtual_coordinates(x, y)
        col = round((x - window_width / 2) / (self.cell_size + self.cell_spacing) + (self.board_width - 1) / 2)
        row = round((y - window_height / 2) / (self.cell_size + self.cell_spacing)
                    + (self.board_height + self.screen_height - 1) / 2)
        return row, col

    def get_position(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        window_width, window_height = director.get_window_size()
        row, col = pos
        x = (col - (self.board_width - 1) / 2) * (self.cell_size + self.cell_spacing) + window_width / 2
        y = (row - (self.board_height + self.screen_height - 1) / 2) \
            * (self.cell_size + self.cell_spacing) + window_height / 2
        return x, y

    # From now on we shall unanimously assume that the first coordinate corresponds to row number (AKA vertical axis).
    def get_cell(self, pos: Tuple[int, int]) -> Sprite:
        return self.board_sprites[pos[0]][pos[1]]

    def get_key(self, pos: Tuple[int, int]) -> Key:
        return self.key_sprites[pos[0]][pos[1]]

    def not_on_board(self, pos: Tuple[int, int]) -> bool:
        return pos[0] < 0 or pos[0] >= self.board_height or pos[1] < 0 or pos[1] >= self.board_width

    def not_a_key(self, pos: Union[None, Tuple[int, int]]) -> bool:
        return pos is None or self.not_on_board(pos) or self.get_key(pos).is_empty()

    def nothing_selected(self) -> bool:
        return self.not_a_key(self.selected_key)

    def not_movable(self, pos: Tuple[int, int]):
        return self.not_a_key(pos)

    def select_key(self, pos: Tuple[int, int]) -> None:
        if self.not_on_board(pos):
            return  # there's nothing to select off the board
        if pos == self.selected_key:
            return  # key already selected, nothing else to do

        # set selection properties for the selected key
        self.selected_key = pos
        self.selection.opacity = 255
        self.selection.position = self.get_position(pos)

        # move the key to active key node (to be displayed on top of everything else)
        key_sprite = self.get_key(self.selected_key)
        self.keys.remove(key_sprite)
        self.active_key.add(key_sprite)
        key_sprite.scale *= self.key_press_scale

    def deselect_key(self) -> None:
        self.selection.opacity = 0

        if self.nothing_selected():
            return

        # move the key to general key node
        key_sprite = self.get_key(self.selected_key)
        key_sprite.scale /= self.key_press_scale
        self.active_key.remove(key_sprite)
        self.keys.add(key_sprite)

        self.selected_key = None

    def copy_key(self, pos: Tuple[int, int]):
        path = self.get_key(pos).get_path()
        Image(filename=path).save(filename="clipboard:")

    def add_key(self, pos: Tuple[int, int]):
        path = self.get_key(pos).get_path()
        if self.image_buffer is None:
            self.image_buffer = Image(filename=path)
        else:
            key_image = Image(filename=path)
            new_buffer = Image(width=self.image_buffer.width + key_image.width, height=self.image_buffer.height)
            new_buffer.composite(self.image_buffer, 0, 0)
            new_buffer.composite(key_image, self.image_buffer.width, 0)
            self.image_buffer = new_buffer
        self.image_buffer.save(filename="clipboard:")

    def on_mouse_press(self, x, y, buttons, modifiers) -> None:
        if buttons & mouse.LEFT:
            pos = self.get_coordinates(x, y)
            self.clicked_key = pos  # we need this in order to discern what are we dragging
            if self.not_movable(pos):
                return
            self.deselect_key()  # just in case we had something previously selected
            self.select_key(pos)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        pos = self.get_coordinates(x + dx, y + dy)
        if self.not_on_board(pos):
            self.highlight.opacity = 0
        else:
            self.highlight.opacity = self.highlight_opacity
            self.highlight.position = self.get_position(pos)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        self.on_mouse_motion(x, y, dx, dy)  # move the highlight as well!

    def on_mouse_release(self, x, y, buttons, modifiers) -> None:
        if buttons & mouse.LEFT:
            if self.nothing_selected():
                return
            self.clicked_key = None
            selected = self.selected_key
            pos = self.get_coordinates(x, y)
            if pos == selected:
                self.add_key(pos)
                self.deselect_key()
                return
            if self.not_on_board(pos):
                pos = selected  # to avoid dragging a key off the board, place it back on its cell

            self.deselect_key()  # remove selection

            if selected == pos:
                return

            key_sprite = self.get_key(selected)
            key_sprite.position = self.get_position(pos)              # place the key on the intended position
            swapped_key = self.get_key(pos)                           # we're gonna swap the keys because uh yes.
            self.keys.remove(swapped_key)                             # remove the key from the end position
            self.key_sprites[pos[0]][pos[1]] = key_sprite             # put the moved key on the end position
            self.key_sprites[selected[0]][selected[1]] = swapped_key  # put the other key on the start position
            swapped_key.position = self.get_position(selected)        # don't forget to update its position! :D
            self.keys.add(swapped_key)                                # and attach it to the key rendering node

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            if modifiers & key.MOD_ACCEL:  # CMD on OSX, CTRL otherwise
                pass

    def run(self):
        pass

    def get_cell_color(self, _):
        return self.cell_color_1


if __name__ == '__main__':
    Keyboard().run()
