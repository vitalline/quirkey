import os
import sys
from importlib import import_module
from importlib.util import find_spec
from io import BytesIO
from itertools import product
from typing import Tuple, Union, List

from cocos import scene
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.sprite import Sprite
from pyglet import image
from pyglet.resource import ResourceNotFoundException
from pyglet.window import key, mouse
from wand.image import Image

import pyperclip

sys.path.append(os.path.abspath(os.getcwd()))


def _box(var):
    return (*var,) if isinstance(var, (List, Tuple)) else (var,)


class Key(Sprite):
    def __init__(self, name: Union[None, str] = None, board: str = 'util', **kwargs):
        board = 'util' if name is None else board
        super().__init__(f'keyboards/assets/{board}/{name}.png', **kwargs)
        self.board = board
        self.name = name

    def get_path(self) -> str:
        return f'keyboards/assets/{self.board}/{self.name}.png'

    def is_empty(self):
        return self.name is None


class Keyboard(ColorLayer):

    def __init__(self, layout_name: str):
        self.is_event_handler = True

        # super boring initialization stuff (bluh bluh)
        layout = import_module(f'keyboards.{layout_name}')
        layout_edit = import_module(f'keyboards.{layout_name}_edit') \
            if find_spec(f'keyboards.{layout_name}_edit') else layout
        self.board_height = layout.board_height if hasattr(layout, 'board_height') else 4
        self.board_width = layout.board_width if hasattr(layout, 'board_width') else 13  # homestuck is alive!!1
        self.screen_height = layout.screen_height if hasattr(layout, 'screen_height') else 4
        self.cell_size = layout.cell_size if hasattr(layout, 'cell_size') else 64
        self.cell_spacing = layout.cell_spacing if hasattr(layout, 'cell_spacing') else 4
        self.border_width = layout.border_width if hasattr(layout, 'border_width') else 16
        self.background_color = layout.background_color if hasattr(layout, 'background_color') else (204, 204, 204)
        self.key_color = layout.key_color if hasattr(layout, 'key_color') else (220, 220, 220)
        self.highlight_color = layout.highlight_color if hasattr(layout, 'highlight_color') else (255, 255, 255)
        self.highlight_opacity = layout.highlight_opacity if hasattr(layout, 'highlight_opacity') else 50
        self.key_press_color = layout.key_press_color if hasattr(layout, 'key_press_color') else self.key_color
        self.key_press_scale = layout.key_press_scale if hasattr(layout, 'key_press_scale') else 1.25
        self.default_key = layout.default_key if hasattr(layout, 'default_key') else None
        self.backspace_key = layout.backspace_key if hasattr(layout, 'backspace_key') else 'backspace'
        self.enter_key = layout.enter_key if hasattr(layout, 'enter_key') else 'enter'
        self.layout_switch_keys = _box(layout.layout_switch_keys) if hasattr(layout, 'layout_switch_keys') else ()
        self.keyboard_switch_keys = _box(layout.keyboard_switch_keys) if hasattr(layout, 'keyboard_switch_keys') else ()
        self.layout = self.extend_layout(layout_edit.layout if hasattr(layout_edit, 'layout') else [[]])
        self.layout_name = layout_name
        self.asset_folder = layout.asset_folder if hasattr(layout, 'asset_folder') else self.layout_name
        self.window_width = self.board_width * (self.cell_size + self.cell_spacing) + self.border_width * 2
        self.window_height = (self.board_height + self.screen_height) * (self.cell_size + self.cell_spacing) \
            + self.border_width * 2
        director.init(width=self.window_width, height=self.window_height, autoscale=False)
        super().__init__(*self.background_color, 1000)

        self.screen_image = None
        self.image_buffer = None
        self.image_history = []
        self.next_key_position = [0, 0]
        self.selected_key = None
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.screen = Key('cell', color=self.key_color, position=(
            (self.window_width / 2),
            (self.board_height + self.screen_height / 2) * (self.cell_size + self.cell_spacing) + self.border_width))
        self.screen.scale_x = (self.window_width - self.border_width * 2) / self.screen.width
        self.screen.scale_y = (self.cell_size + self.cell_spacing) * self.screen_height / self.screen.height
        self.highlight = Key('cell', color=self.highlight_color, opacity=0)
        self.highlight.scale = self.cell_size / self.highlight.width
        self.selection = Key('cell', color=self.key_press_color, opacity=0)
        self.selection.scale = self.cell_size / self.selection.width * self.key_press_scale
        self.keys = BatchNode()
        self.active_key = BatchNode()
        self.add(self.board, z=1)
        self.add(self.highlight, z=2)
        self.add(self.keys, z=3)
        self.add(self.active_key, z=3)
        self.board.add(self.screen)
        self.active_key.add(self.selection)

        for row in range(self.board_height):
            self.board_sprites = [[Key('cell') for _ in range(self.board_width)] for _ in range(self.board_height)]
            self.key_sprites = [[Key() for _ in range(self.board_width)] for _ in range(self.board_height)]

        for row, col in product(range(self.board_height), range(self.board_width)):

            self.board_sprites[row][col].position = self.get_position((row, col))
            self.board_sprites[row][col].scale = self.cell_size / self.board_sprites[row][col].width
            self.board_sprites[row][col].color = self.get_cell_color((row, col))
            self.board.add(self.board_sprites[row][col])

        self.sublayout = 0
        self.update_layout()

        director.run(scene.Scene(self))

    def update_layout(self):
        for row, col in product(range(self.board_height), range(self.board_width)):
            if self.key_sprites[row][col].parent == self.keys:
                self.keys.remove(self.key_sprites[row][col])
            try:
                self.key_sprites[row][col] = Key(self.layout[self.sublayout][row][col], self.asset_folder)
            except (IndexError, ResourceNotFoundException):
                if self.default_key:
                    self.key_sprites[row][col] = Key(self.default_key, self.asset_folder)
                else:
                    self.key_sprites[row][col] = Key()
            finally:
                if self.key_sprites[row][col].is_empty():
                    self.board_sprites[row][col].opacity = 0
                else:
                    self.board_sprites[row][col].opacity = 255

            self.key_sprites[row][col].position = self.get_position((row, col))
            self.key_sprites[row][col].scale = self.cell_size / self.key_sprites[row][col].width
            self.keys.add(self.key_sprites[row][col])

    def get_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        x, y = director.get_virtual_coordinates(x, y)
        col = round((x - self.window_width / 2) / (self.cell_size + self.cell_spacing)
                    + (self.board_width - 1) / 2)
        row = round((self.board_height - self.screen_height - 1) / 2
                    - (y - self.window_height / 2) / (self.cell_size + self.cell_spacing))
        return row, col

    def get_position(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        row, col = pos
        x = (col - (self.board_width - 1) / 2) \
            * (self.cell_size + self.cell_spacing) + self.window_width / 2
        y = ((self.board_height - self.screen_height - 1) / 2 - row) \
            * (self.cell_size + self.cell_spacing) + self.window_height / 2
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

    def select_key(self, pos: Tuple[int, int]) -> None:
        if self.not_a_key(pos):
            return  # we shouldn't select a nonexistent key
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

    def copy_key(self, pos: Tuple[int, int]) -> None:
        path = self.get_key(pos).get_path()
        Image(filename=path).save(filename='clipboard:')

    def press_key(self, pos: Tuple[int, int]) -> None:
        pressed_key = self.get_key(pos)
        path = self.get_key(pos).get_path()
        self.image_history.append((self.image_buffer, self.next_key_position))
        if pressed_key.name == self.enter_key:
            # TODO: add support for start/end/double enters
            self.next_key_position = [0, self.image_buffer.height if self.image_buffer is not None else 0]
            return
        elif self.image_buffer is None:
            self.image_buffer = Image(filename=path)
            self.next_key_position = [self.image_buffer.width, 0]
        else:
            key_image = Image(filename=path)
            dx, dy = key_image.size
            new_buffer = Image(width=max(self.image_buffer.width, self.next_key_position[0] + dx),
                               height=max(self.image_buffer.height, self.next_key_position[1] + dy))
            new_buffer.composite(self.image_buffer, 0, 0)
            new_buffer.composite(key_image, *self.next_key_position)
            new_buffer.format = 'png'
            self.image_buffer = new_buffer
            self.next_key_position = [self.next_key_position[0] + dx, self.next_key_position[1]]
        self.update_image()

    def update_image(self):
        if self.image_buffer is None:
            if self.screen_image is not None:
                self.keys.remove(self.screen_image)
            self.screen_image = None
            pyperclip.copy('')
        data_buffer = BytesIO()
        self.image_buffer.save(file=data_buffer)
        data_buffer.seek(0)
        screen_image = image.load('temp.png', file=data_buffer)
        if self.screen_image is not None:
            self.keys.remove(self.screen_image)
        self.screen_image = Sprite(image=screen_image,
                                   position=(self.border_width, self.window_height - self.border_width),
                                   anchor=(0, screen_image.height))
        self.screen_image.scale = min(self.screen.width / self.screen_image.width,
                                      self.screen.height / self.screen_image.height,
                                      1)
        self.keys.add(self.screen_image)
        self.image_buffer.save(filename='clipboard:')

    def extend_layout(self, layout: List[List[List[str]]]):
        new_layout = [[['' for _ in range(self.board_width)]
                       for _ in range(self.board_height)]
                      for _ in range(len(layout))]
        for sub in range(len(new_layout)):
            for row in range(len(new_layout[sub])):
                for col in range(len(new_layout[sub][row])):
                    try:
                        new_layout[sub][row][col] = layout[sub][row][col]
                    except IndexError:
                        pass
        return new_layout

    def pretty_layout(self):
        endl = '\n'
        return '[\n' + [''.join(
            '    [\n' + f"{''.join([f'        {repr(row)},{endl}' for row in sub])}" +
            '    ],\n' for sub in self.layout
        )][0] + ']'

    def on_mouse_press(self, x, y, buttons, modifiers) -> None:
        if buttons & (mouse.LEFT | mouse.RIGHT):
            pos = self.get_coordinates(x, y)
            if self.not_a_key(pos):
                return
            self.deselect_key()  # just in case we had something previously selected
            self.select_key(pos)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        pos = self.get_coordinates(x + dx, y + dy)
        if self.not_a_key(pos):
            self.highlight.opacity = 0
        else:
            self.highlight.opacity = self.highlight_opacity
            self.highlight.position = self.get_position(pos)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        self.on_mouse_motion(x, y, dx, dy)  # move the highlight as well!

    def on_mouse_release(self, x, y, buttons, modifiers) -> None:
        if self.nothing_selected():
            return
        if buttons & (mouse.LEFT | mouse.RIGHT):
            selected = self.selected_key
            pos = self.get_coordinates(x, y)
            if pos == selected:
                self.deselect_key()
                key_name = self.get_key(pos).name
                if key_name in self.layout_switch_keys:
                    self.deselect_key()
                    if (len(self.layout) > 1 and key_name == self.layout_switch_keys[0]) == (buttons & mouse.LEFT):
                        self.sublayout = (self.sublayout + len(self.layout) - 1) % len(self.layout)
                    else:
                        self.sublayout = (self.sublayout + 1) % len(self.layout)
                    self.update_layout()
                    return
                elif key_name == self.backspace_key:
                    if len(self.image_history) == 0:
                        return
                    if buttons & mouse.LEFT:
                        self.image_buffer, self.next_key_position = self.image_history.pop()
                    elif buttons & mouse.RIGHT:
                        self.image_buffer, self.next_key_position = self.image_history[0]
                        self.image_history.clear()
                    self.update_image()
                else:
                    self.press_key(pos)
                return
            if self.not_on_board(pos):
                pos = selected  # to avoid dragging a key off the board, place it back on its cell

            self.deselect_key()  # remove selection

            if selected == pos:
                return

            key_sprite = self.get_key(selected)
            key_sprite.position = self.get_position(pos)
            swapped_key = self.get_key(pos)
            swapped_key.position = self.get_position(selected)
            self.key_sprites[pos[0]][pos[1]] = key_sprite
            self.key_sprites[selected[0]][selected[1]] = swapped_key
            if swapped_key.is_empty():
                self.board_sprites[pos[0]][pos[1]].opacity = 255
                self.board_sprites[selected[0]][selected[1]].opacity = 0
            swapped_key = self.layout[self.sublayout][pos[0]][pos[1]]
            self.layout[self.sublayout][pos[0]][pos[1]] = self.layout[self.sublayout][selected[0]][selected[1]]
            self.layout[self.sublayout][selected[0]][selected[1]] = swapped_key

            # print(self.pretty_layout())
            layout_edit = open(f'keyboards/{self.layout_name}_edit.py', 'w')
            layout_edit.write(f'layout = {self.pretty_layout()}')
            layout_edit.close()

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol == key.R:
            if modifiers & key.MOD_ACCEL:  # CMD on OSX, CTRL otherwise
                pass

    def run(self):
        pass

    def get_cell_color(self, _):
        return self.key_color


if __name__ == '__main__':
    Keyboard('hs').run()
