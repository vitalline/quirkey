import configparser
import os
import sys
from glob import iglob
from importlib import import_module
from importlib.util import find_spec
from io import BytesIO
from itertools import product
from math import ceil, sqrt
from typing import Any, Optional, Union

import win32clipboard as clp
from PIL import Image
from PIL.ImageColor import getrgb
from cocos import scene
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer, MultiplexLayer
from cocos.sprite import Sprite
from pyglet import image
from pyglet.window import key, mouse

import pyperclip

sys.path.append(os.path.abspath(os.getcwd()))

color = tuple[int, int, int]


def box(var):
    return (*var,) if isinstance(var, (list, tuple)) else (var,)


def copyattr(self: object, obj: object, k: str, default: Optional[Any] = None):
    setattr(self, k, getattr(obj, k, default))


class Key(Sprite):
    def __init__(self, name: Union[None, str, list[Union[str, list[str]]]] = None, board: str = 'util',
                 size: Union[None, int, float, tuple[Union[int, float], Union[int, float]]] = None, **kwargs):
        self.empty = False
        if name in (None, []):
            self.empty = True
            name = 'none'
            board = 'util'
        self.name = name
        self.board = board
        if type(name) == list:
            if type(name[0]) == list:
                grid_height = len(name)
                grid_width = max(len(row) for row in name)
                new_name = [string for row in name for string in (row + [''] * (len(row) - grid_width))]
            else:
                grid_width = ceil(sqrt(len(name)))
                grid_height = ceil(len(name) / grid_width)
                new_name = name[:] + [''] * (len(name) - grid_width * grid_height)
            if size is None:
                size = 64 * grid_width, 64 * grid_height
            elif type(size) in (int, float):
                size = size, size
            image_buffer = Image.new(mode='RGBA', size=size, color=(0, 0, 0, 0))
            for i, subname in enumerate(new_name):
                subimage = Image.open(self.get_path(subname))
                subimage = subimage.resize((size[0] // grid_width, size[1] // grid_width))
                image_buffer.paste(subimage, (
                    round(subimage.width * (i % grid_width)),
                    round(subimage.height * (i // grid_width + (grid_width - grid_height) / 2))
                ))
            data_buffer = BytesIO()
            image_buffer.save(data_buffer, format='png')
            data_buffer.seek(0)
            super().__init__(image.load('temp.png', file=data_buffer), **kwargs)
        else:
            super().__init__(self.get_path(), **kwargs)
            if size is None:
                size = self.width, self.height
            elif type(size) in (int, float):
                size = size, size
        self.resize(*size)

    def get_path(self, name: str = None, board: str = None, update: bool = False) -> str:
        if name is None:
            name = self.name
        if board is None:
            board = self.board
        path_string = 'keyboards/assets/{}/{}.png'
        if not os.path.isfile(path_string.format(board, name)):
            if board == self.board and name == self.name:
                self.empty = True
            board, name = 'util', 'none'
        return path_string.format(board, name)

    def is_empty(self) -> bool:
        return self.empty

    def resize(self, width: Union[int, float], height: Union[None, int, float] = None) -> None:
        if height is None:
            height = width
        self.scale_x = width * self.scale_x / self.width
        self.scale_y = height * self.scale_y / self.height


class KeyboardManager(MultiplexLayer):
    def __init__(self):
        self.screen_image = None
        self.image_buffer = None
        self.image_history = []
        self.next_key_position = [0, 0]
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        try:
            load_order = [name.strip() for name in self.config.get('Keyboard Settings', 'load_order').split(',')
                          if name.strip()]
        except configparser.Error:
            load_order = [name[10:-3] for name in iglob('keyboards/*.py')]
        self.load_value('key_size', 64)
        self.load_value('key_spacing', 4)
        self.load_value('border_width', 16)
        self.load_value('background_color', (204, 204, 204))
        self.load_value('key_color', (220, 220, 220))
        self.load_value('screen_color', (220, 220, 220))
        self.load_value('highlight_color', (255, 255, 255))
        self.load_value('highlight_opacity', 50)
        self.load_value('key_press_color', self.key_color)
        self.load_value('key_press_scale', 1.25)
        self.load_value('cursor_color', self.highlight_color)
        self.load_value('cursor_opacity', self.highlight_opacity)
        layers = [Keyboard(name, self) for name in load_order]
        director.init(width=layers[0].window_width, height=layers[0].window_height, autoscale=False)
        super().__init__(*layers)
        for layer in layers:
            layer.post_init()

    def load_value(self, k: str, default: Any) -> None:
        value = self.config.get('Keyboard Settings', k, fallback=default)
        if type(default) == tuple and len(default) == 3:  # we just kinda *assume* this is a color
            setattr(self, k, getrgb(value)[:3])
        else:
            setattr(self, k, type(default)(value))

    def run(self):
        director.run(scene.Scene(self))

    def switch_to(self, layer_number: int):
        if self.screen_image is not None \
                and self.screen_image.parent == self.layers[self.enabled_layer] \
                and self.enabled_layer != layer_number:
            self.layers[self.enabled_layer].remove(self.screen_image)
        super().switch_to(layer_number)
        self.layers[layer_number].update_image()
        director.window.set_size(self.layers[layer_number].window_width, self.layers[layer_number].window_height)


class Keyboard(ColorLayer):

    def __init__(self, layout_name: str, manager: KeyboardManager):
        # super boring initialization stuff (bluh bluh)
        self.manager = manager
        self.is_event_handler = True

        copyattr(self, self.manager, 'screen_height')
        copyattr(self, self.manager, 'key_size')
        copyattr(self, self.manager, 'key_spacing')
        copyattr(self, self.manager, 'border_width')
        copyattr(self, self.manager, 'background_color')
        copyattr(self, self.manager, 'key_color')
        copyattr(self, self.manager, 'screen_color')
        copyattr(self, self.manager, 'highlight_color')
        copyattr(self, self.manager, 'highlight_opacity')
        copyattr(self, self.manager, 'key_press_color')
        copyattr(self, self.manager, 'key_press_scale')
        copyattr(self, self.manager, 'cursor_color')
        copyattr(self, self.manager, 'cursor_opacity')

        layout = import_module(f'keyboards.{layout_name}')
        layout_edit = import_module(f'keyboards.{layout_name}_edit') \
            if find_spec(f'keyboards.{layout_name}_edit') else layout
        copyattr(self, layout, 'board_height', 0)
        copyattr(self, layout, 'board_width', 0)
        copyattr(self, layout, 'screen_height', 3)
        copyattr(self, layout, 'default_key', None)
        copyattr(self, layout, 'backspace_key', 'backspace')
        copyattr(self, layout, 'enter_key', 'enter')
        copyattr(self, layout, 'preview_key', None)
        copyattr(self, layout, 'keyboard_switch_keys', ())
        copyattr(self, layout, 'layout_switch_keys', ())
        copyattr(self, layout, 'default_layout', 0)
        copyattr(self, layout, 'asset_folder', layout_name)
        self.layout_name = layout_name
        self.layout = self.extend_layout(layout_edit.layout if hasattr(layout_edit, 'layout') else [[]])
        self.window_width = self.board_width * (self.key_size + self.key_spacing) + self.border_width * 2
        self.window_height = (self.board_height + self.screen_height) * (self.key_size + self.key_spacing) \
            + self.border_width * 2

    def post_init(self):
        super().__init__(*self.background_color, 1000, self.window_width, self.window_height)
        self.selected_key = None
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.screen = Key('cell', color=self.screen_color, position=(
            (self.window_width / 2),
            (self.board_height + self.screen_height / 2) * (self.key_size + self.key_spacing) + self.border_width))
        self.screen.resize((self.window_width - self.border_width * 2),
                           (self.key_size + self.key_spacing) * self.screen_height)
        self.highlight = Key('cell', size=self.key_size, color=self.highlight_color, opacity=0)
        self.selection = Key('cell', size=self.key_size * self.key_press_scale, color=self.key_press_color, opacity=0)
        self.cursor = Key('cell', size=self.key_size, color=self.cursor_color, opacity=self.cursor_opacity,
                          position=(self.border_width, self.window_height - self.border_width),
                          anchor=(0, self.key_size / 2))
        self.keys = BatchNode()
        self.overlay = BatchNode()
        self.active_key = BatchNode()
        self.add(self.board, z=1)
        self.add(self.highlight, z=2)
        self.add(self.keys, z=3)
        self.add(self.overlay, z=4)
        self.add(self.active_key, z=5)
        self.board.add(self.screen)
        self.overlay.add(self.selection)
        self.overlay.add(self.cursor)

        for row in range(self.board_height):
            self.board_sprites = [[Key('cell', size=self.key_size) for _ in range(self.board_width)]
                                  for _ in range(self.board_height)]
            self.key_sprites = [[Key() for _ in range(self.board_width)] for _ in range(self.board_height)]

        for row, col in product(range(self.board_height), range(self.board_width)):

            self.board_sprites[row][col].position = self.get_position((row, col))
            self.board_sprites[row][col].color = self.get_cell_color((row, col))
            self.board.add(self.board_sprites[row][col])

        self.sublayout = self.default_layout
        self.update_layout()

    def update_layout(self):
        preview_keys = [board.preview_key if hasattr(board, 'preview_key') else None for board in self.manager.layers]
        layer_index = self.manager.layers.index(self)
        layer_count = len(self.manager.layers)
        if len(self.keyboard_switch_keys) == 1:
            new_keyboard_switch_keys = (preview_keys[(layer_index + 1) % layer_count])
        else:
            new_keyboard_switch_keys = (preview_keys[(layer_index + layer_count - 1) % layer_count],
                                        preview_keys[(layer_index + 1) % layer_count])
        for row, col in product(range(self.board_height), range(self.board_width)):
            if self.key_sprites[row][col].parent == self.keys:
                self.keys.remove(self.key_sprites[row][col])
            old_name = self.layout[self.sublayout][row][col]
            new_name = old_name
            if new_name in self.keyboard_switch_keys:
                replacement_key = new_keyboard_switch_keys[self.keyboard_switch_keys.index(new_name)]
                if replacement_key is not None:
                    new_name = replacement_key
            new_sprite = Key(new_name, self.asset_folder)
            if new_name != old_name:
                new_sprite.name = old_name
            new_sprite.position = self.get_position((row, col))
            new_sprite.resize(self.key_size)
            self.board_sprites[row][col].opacity = 0 if new_sprite.is_empty() else 255
            self.key_sprites[row][col] = new_sprite
            self.keys.add(self.key_sprites[row][col])

    @property
    def screen_image(self) -> Optional[Sprite]:
        return self.manager.screen_image

    @screen_image.setter
    def screen_image(self, value: Optional[Sprite]) -> None:
        self.manager.screen_image = value

    @property
    def image_buffer(self) -> Optional[Image.Image]:
        return self.manager.image_buffer

    @image_buffer.setter
    def image_buffer(self, value: Optional[Image.Image]) -> None:
        self.manager.image_buffer = value

    @property
    def image_history(self) -> list[tuple[Optional[Image.Image], list[int]]]:
        return self.manager.image_history

    @property
    def next_key_position(self) -> list[int]:
        return self.manager.next_key_position

    @next_key_position.setter
    def next_key_position(self, value: list[int]) -> None:
        self.manager.next_key_position = value

    def get_coordinates(self, x: float, y: float) -> tuple[int, int]:
        x, y = director.get_virtual_coordinates(x, y)
        col = round((x - self.window_width / 2) / (self.key_size + self.key_spacing)
                    + (self.board_width - 1) / 2)
        row = round((self.board_height - self.screen_height - 1) / 2
                    - (y - self.window_height / 2) / (self.key_size + self.key_spacing))
        return row, col

    def get_position(self, pos: tuple[int, int]) -> tuple[float, float]:
        row, col = pos
        x = (col - (self.board_width - 1) / 2) \
            * (self.key_size + self.key_spacing) + self.window_width / 2
        y = ((self.board_height - self.screen_height - 1) / 2 - row) \
            * (self.key_size + self.key_spacing) + self.window_height / 2
        return x, y

    # From now on we shall unanimously assume that the first coordinate corresponds to row number (AKA vertical axis).
    def get_cell(self, pos: tuple[int, int]) -> Sprite:
        return self.board_sprites[pos[0]][pos[1]]

    def get_key(self, pos: tuple[int, int]) -> Key:
        return self.key_sprites[pos[0]][pos[1]]

    def not_on_board(self, pos: tuple[int, int]) -> bool:
        return pos[0] < 0 or pos[0] >= self.board_height or pos[1] < 0 or pos[1] >= self.board_width

    def not_a_key(self, pos: Union[None, tuple[int, int]]) -> bool:
        return pos is None or self.not_on_board(pos) or self.get_key(pos).is_empty()

    def nothing_selected(self) -> bool:
        return self.not_a_key(self.selected_key)

    def select_key(self, pos: tuple[int, int]) -> None:
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
        key_sprite.resize(self.key_size * self.key_press_scale)

    def deselect_key(self) -> None:
        self.selection.opacity = 0

        if self.nothing_selected():
            return

        # move the key to general key node
        key_sprite = self.get_key(self.selected_key)
        key_sprite.resize(self.key_size)
        self.active_key.remove(key_sprite)
        self.keys.add(key_sprite)

        self.selected_key = None

    def press_key(self, pos: tuple[int, int]) -> None:
        self.image_history.append((self.image_buffer, self.next_key_position.copy()))
        pressed_key = self.get_key(pos)
        if pressed_key.name == self.enter_key:
            self.next_key_position = [0, self.next_key_position[1] + self.key_size]
            key_image = Key().image
        else:
            key_image = pressed_key.image
        image_buffer = BytesIO()
        key_image.save('temp.png', file=image_buffer)
        image_buffer.seek(0)
        key_image = Image.open(image_buffer).resize((self.key_size, self.key_size))
        if self.image_buffer is None:
            self.image_buffer = key_image
            if pressed_key.name != self.enter_key:
                self.next_key_position = [self.image_buffer.width, 0]
        else:
            new_buffer = Image.new(
                mode='RGBA',
                size=(max(self.image_buffer.width, self.next_key_position[0] + self.key_size),
                      max(self.image_buffer.height, self.next_key_position[1] + self.key_size)),
                color=(0, 0, 0, 0)
            )
            new_buffer.paste(self.image_buffer)
            new_buffer.paste(key_image, self.next_key_position.copy())
            self.image_buffer = new_buffer
            if pressed_key.name != self.enter_key:
                self.next_key_position[0] += self.key_size
        self.update_image()

    def update_image(self):
        if self.image_buffer is None:
            if self.screen_image is not None and self.screen_image.parent == self:
                self.remove(self.screen_image)
            self.screen_image = None
            self.cursor.position = (self.border_width, self.window_height - self.border_width)
            self.cursor.scale = 1
            pyperclip.copy('')
            return
        data_buffer = BytesIO()
        self.image_buffer.save(data_buffer, format='png')
        data_buffer.seek(0)
        screen_image = image.load('temp.png', file=data_buffer)
        if self.screen_image is not None and self.screen_image.parent == self:
            self.remove(self.screen_image)
        self.screen_image = Sprite(image=screen_image,
                                   position=(self.border_width,
                                             self.window_height - self.border_width - self.key_spacing),
                                   anchor=(0, screen_image.height))
        self.screen_image.scale = min(self.screen.width / (self.screen_image.width + self.key_size),
                                      self.screen.height / self.screen_image.height,
                                      1)
        self.add(self.screen_image, z=3)
        self.cursor.position = (self.border_width + self.next_key_position[0] * self.screen_image.scale,
                                self.window_height - self.border_width
                                - self.next_key_position[1] * self.screen_image.scale)
        self.cursor.scale = self.screen_image.scale
        save_path = 'saved.png'
        self.image_buffer.save(save_path)  # in case my clipboard shenanigans don't work just use the file ig
        save_path = os.path.abspath(save_path).encode('utf-16-le') + b'\0'
        data_buffer.seek(0)
        clp.OpenClipboard()
        clp.EmptyClipboard()
        clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), save_path)
        clp.SetClipboardData(clp.RegisterClipboardFormat('image/png'), data_buffer.getvalue())
        clp.CloseClipboard()

    def extend_layout(self, layout: list[list[list[str]]]):
        if self.board_height == 0:
            self.board_height = max(len(sub) for sub in layout)
        if self.board_width == 0:
            self.board_width = max(len(row) for sub in layout for row in sub)
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

    def on_mouse_press(self, x, y, buttons, _modifiers) -> None:
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

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers) -> None:
        self.on_mouse_motion(x, y, dx, dy)  # move the highlight as well!

    def on_mouse_release(self, x, y, buttons, _modifiers) -> None:
        if self.nothing_selected():
            return
        if buttons & (mouse.LEFT | mouse.RIGHT):
            pos = self.get_coordinates(x, y)
            selected = self.selected_key
            self.deselect_key()
            if pos == selected:
                key_name = self.get_key(pos).name
                if key_name in self.keyboard_switch_keys:
                    length = len(self.manager.layers)
                    if len(self.keyboard_switch_keys) > 1 and key_name == self.keyboard_switch_keys[0]:
                        self.manager.switch_to((self.manager.enabled_layer + length - 1) % length)
                    else:
                        self.manager.switch_to((self.manager.enabled_layer + 1) % length)
                    return
                elif key_name in self.layout_switch_keys:
                    if type(key_name) == list:
                        self.sublayout = self.layout_switch_keys.index(key_name)
                        self.update_layout()
                    else:
                        length = len(self.layout)
                        if (len(self.layout_switch_keys) > 1 and key_name == self.layout_switch_keys[0]) \
                                == (buttons & mouse.LEFT):
                            self.sublayout = (self.sublayout + length - 1) % length
                        else:
                            self.sublayout = (self.sublayout + 1) % length
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
        director.run(scene.Scene(self))

    def get_cell_color(self, _):
        return self.key_color


if __name__ == '__main__':
    KeyboardManager().run()
