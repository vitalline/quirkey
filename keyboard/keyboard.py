from importlib import import_module
from importlib.util import find_spec
from io import BytesIO
from itertools import product
from os.path import abspath, isfile
from typing import Union, TYPE_CHECKING

import win32clipboard as clp
from PIL import Image
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.sprite import Sprite
from pyglet.image import load
from pyglet.window import key, mouse

import pyperclip
from keyboard.key import Key

if TYPE_CHECKING:
    from keyboard.manager import KeyboardManager


class Keyboard(ColorLayer):

    def __init__(self, name: str, manager: 'KeyboardManager'):
        # super boring initialization stuff
        self.manager = manager
        self.is_event_handler = True

        layout = import_module(f'keyboards.{name}')
        layout_edit = import_module(f'keyboards.{name}_edit') \
            if find_spec(f'keyboards.{name}_edit') and isfile(f'keyboards/{name}_edit.py') else layout
        self.board_height = getattr(layout, 'board_height', 0)
        self.board_width = getattr(layout, 'board_width', 0)
        self.screen_height = getattr(layout, 'screen_height', 3)
        self.backspace_key = getattr(layout, 'backspace_key', 'backspace')
        self.enter_key = getattr(layout, 'enter_key', 'enter')
        self.preview_keys = getattr(layout, 'preview_keys', dict())
        self.asset_folder = getattr(layout, 'asset_folder', name)
        self.name = name
        self.layouts = self.extend_layout(layout_edit.layouts if hasattr(layout_edit, 'layouts') else {'': [[]]})
        self.default_layout = getattr(layout, 'default_layout', sorted(self.layouts.keys())[0])
        self.postprocess = getattr(layout, 'postprocess', lambda image: image.copy())
        self.window_width = self.board_width \
            * (self.manager.key_size + self.manager.key_spacing) \
            + self.manager.border_width * 2
        self.window_height = (self.board_height + self.screen_height) \
            * (self.manager.key_size + self.manager.key_spacing) \
            + self.manager.border_width * 2
        super().__init__(*self.manager.app_color, self.window_width, self.window_height)
        self.selected_key = None
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.screen = Key(
            'cell',
            color=self.manager.screen_color[:3],
            opacity=self.manager.screen_color[3],
            position=(
                (self.window_width / 2),
                (self.board_height + self.screen_height / 2)
                * (self.manager.key_size + self.manager.key_spacing)
                + self.manager.border_width
            )
        )
        self.screen.resize(
            (self.manager.key_size + self.manager.key_spacing) * self.screen_height,
            (self.window_width - self.manager.border_width * 2)
        )
        self.highlight = Key(
            'cell',
            size=self.manager.key_size,
            color=self.manager.highlight_color[:3],
            opacity=0
        )
        self.pressed_key = Key(
            'cell',
            size=self.manager.key_size * self.manager.pressed_key_scale,
            color=self.manager.pressed_key_color[:3], opacity=0
        )
        self.cursor = Key(
            'cursor',
            size=self.manager.key_size,
            color=self.manager.cursor_color[:3],
            opacity=self.manager.cursor_color[3],
            position=(self.manager.border_width, self.window_height - self.manager.border_width),
            anchor=(0, self.manager.key_size / 2)
        )
        self.keys = BatchNode()
        self.overlay = BatchNode()
        self.active_key = BatchNode()
        self.add(self.board, z=1)
        self.add(self.highlight, z=2)
        self.add(self.keys, z=3)
        self.add(self.overlay, z=4)
        self.add(self.active_key, z=5)
        self.board.add(self.screen)
        self.overlay.add(self.pressed_key)
        self.overlay.add(self.cursor)
        for row in range(self.board_height):
            self.board_sprites = [[Key('cell', size=self.manager.key_size) for _ in range(self.board_width)]
                                  for _ in range(self.board_height)]
            self.key_sprites = [[Key() for _ in range(self.board_width)] for _ in range(self.board_height)]

        for row, col in product(range(self.board_height), range(self.board_width)):

            self.board_sprites[row][col].position = self.get_position((row, col))
            self.board_sprites[row][col].color = self.manager.key_color[:3]
            self.board_sprites[row][col].opacity = self.manager.key_color[3]
            self.board.add(self.board_sprites[row][col])

        self.current_layout = self.default_layout

    def update_layout(self):
        for row, col in product(range(self.board_height), range(self.board_width)):
            if self.key_sprites[row][col].parent == self.keys:
                self.keys.remove(self.key_sprites[row][col])
            old_name = self.layouts[self.current_layout][row][col]
            path_name = old_name.split(':')[0]
            layout_name = path_name.split('/')[0]
            for name in old_name, path_name, layout_name:
                if name in self.manager.preview_keys:
                    _, keyboard = self.manager.get_keyboard(layout_name)
                    asset_folder = keyboard.asset_folder if keyboard is not None else self.asset_folder
                    new_name = self.manager.preview_keys[name]
                    new_sprite = Key(new_name, asset_folder)
                    new_sprite.rename(old_name)
                    break
            else:
                if old_name in self.preview_keys:
                    new_sprite = Key(self.preview_keys[old_name], self.asset_folder)
                    new_sprite.rename(old_name)
                else:
                    new_sprite = Key(old_name, self.asset_folder)
            new_sprite.position = self.get_position((row, col))
            new_sprite.resize(self.manager.key_size)
            self.board_sprites[row][col].opacity = 0 if new_sprite.is_empty() else self.manager.key_color[3]
            self.key_sprites[row][col] = new_sprite
            self.keys.add(self.key_sprites[row][col])

    def get_coordinates(self, x: float, y: float) -> tuple[int, int]:
        x, y = director.get_virtual_coordinates(x, y)
        col = round((x - self.window_width / 2) / (self.manager.key_size + self.manager.key_spacing)
                    + (self.board_width - 1) / 2)
        row = round((self.board_height - self.screen_height - 1) / 2
                    - (y - self.window_height / 2) / (self.manager.key_size + self.manager.key_spacing))
        return row, col

    def get_position(self, pos: tuple[int, int]) -> tuple[float, float]:
        row, col = pos
        x = (col - (self.board_width - 1) / 2) \
            * (self.manager.key_size + self.manager.key_spacing) + self.window_width / 2
        y = ((self.board_height - self.screen_height - 1) / 2 - row) \
            * (self.manager.key_size + self.manager.key_spacing) + self.window_height / 2
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
        self.pressed_key.opacity = self.manager.pressed_key_color[3]
        self.pressed_key.position = self.get_position(pos)

        # move the key to active key node (to be displayed on top of everything else)
        key_sprite = self.get_key(self.selected_key)
        self.keys.remove(key_sprite)
        self.active_key.add(key_sprite)
        key_sprite.resize(self.manager.key_size * self.manager.pressed_key_scale)

    def deselect_key(self) -> None:
        self.pressed_key.opacity = 0

        if self.nothing_selected():
            return

        # move the key to general key node
        key_sprite = self.get_key(self.selected_key)
        key_sprite.resize(self.manager.key_size)
        self.active_key.remove(key_sprite)
        self.keys.add(key_sprite)

        self.selected_key = None

    def press_key(self, pos: tuple[int, int]) -> None:
        self.manager.image_history.append((self.manager.image_buffer, self.manager.next_key_position.copy()))
        pressed_key = self.get_key(pos)
        if pressed_key.name == self.enter_key:
            self.manager.next_key_position = [0, self.manager.next_key_position[1] + self.manager.key_size]
            key_image = Key().image
        else:
            key_image = pressed_key.image
        image_buffer = BytesIO()
        key_image.save('temp.png', file=image_buffer)
        image_buffer.seek(0)
        key_image = Image.open(image_buffer)
        key_image = key_image.resize(
            (round(key_image.width * self.manager.key_size / key_image.height),
             self.manager.key_size)
        )
        if self.manager.image_buffer is None:
            self.manager.image_buffer = key_image
            if pressed_key.name != self.enter_key:
                self.manager.next_key_position = [self.manager.image_buffer.width, 0]
        else:
            new_buffer = Image.new(
                mode='RGBA',
                size=(max(self.manager.image_buffer.width, self.manager.next_key_position[0] + key_image.width),
                      max(self.manager.image_buffer.height, self.manager.next_key_position[1] + self.manager.key_size)),
                color=(0, 0, 0, 0)
            )
            new_buffer.paste(self.manager.image_buffer)
            new_buffer.paste(key_image, self.manager.next_key_position.copy())
            self.manager.image_buffer = new_buffer
            if pressed_key.name != self.enter_key:
                self.manager.next_key_position[0] += key_image.width
        self.update_image()

    def update_image(self):
        if self.manager.image_buffer is None:
            if self.manager.screen_image is not None and self.manager.screen_image.parent == self:
                self.remove(self.manager.screen_image)
            self.manager.screen_image = None
            self.cursor.position = (self.manager.border_width, self.window_height - self.manager.border_width)
            self.cursor.resize(self.manager.key_size)
            pyperclip.copy('')
            return

        data_buffer = BytesIO()
        self.manager.image_buffer.save(data_buffer, format='png')
        data_buffer.seek(0)

        screen_image = load('temp.png', file=data_buffer)
        if self.manager.screen_image is not None and self.manager.screen_image.parent == self:
            self.remove(self.manager.screen_image)
        self.manager.screen_image = Sprite(
            image=screen_image,
            position=(
                self.manager.border_width,
                self.window_height - self.manager.border_width - self.manager.key_spacing
            ),
            anchor=(0, screen_image.height)
        )
        self.manager.screen_image.scale = min(
            self.screen.width / (self.manager.screen_image.width + self.cursor.width),
            self.screen.height / self.manager.screen_image.height,
            1
        )
        self.add(self.manager.screen_image, z=3)
        self.cursor.position = (
            self.manager.border_width + self.manager.next_key_position[0] * self.manager.screen_image.scale,
            self.window_height - self.manager.border_width
            - self.manager.next_key_position[1] * self.manager.screen_image.scale
        )
        self.cursor.resize(self.manager.key_size * self.manager.screen_image.scale)

        post_processed_image = self.postprocess(self.manager.image_buffer)

        background_image = Image.new(
            mode='RGBA',
            size=(post_processed_image.width, post_processed_image.height),
            color=self.manager.image_color  # for anyone who can't use transparency for some weird tech-related reason
        )
        background_image.alpha_composite(post_processed_image)
        opaque_image = background_image.copy()
        opaque_image.mode = 'RGB'

        path = 'regular.png'
        background_image.save(path)   # in case my clipboard shenanigans don't work, use the file itself

        path = 'opaque.png'
        opaque_image.save(path)   # or use this file if you're having transparency issues

        path = 'transparent.png'
        self.manager.image_buffer.save(path)  # or this one if you want to edit in a background or something

        copy_path = abspath(f'{self.manager.output_mode}.png').encode('utf-16-le') + b'\0'
        copy_file = open(f'{self.manager.output_mode}.png', 'rb')

        clp.OpenClipboard()
        clp.EmptyClipboard()  # You may have seen this on https://stackoverflow.com/q/66845295/17391024. You're welcome.
        clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), copy_path)         # works for Discord
        clp.SetClipboardData(clp.RegisterClipboardFormat('image/png'), copy_file.read())  # works for PDN & TG
        clp.CloseClipboard()

    def extend_layout(self, layout: dict):
        if self.board_height == 0:
            self.board_height = max(len(layout[k]) for k in layout)
        if self.board_width == 0:
            self.board_width = max(len(row) for k in layout for row in layout[k])
        new_layout = {k: [['' for _ in range(self.board_width)]
                      for _ in range(self.board_height)]
                      for k in layout.keys()}
        for k in new_layout.keys():
            for row in range(len(new_layout[k])):
                for col in range(len(new_layout[k][row])):
                    try:
                        new_layout[k][row][col] = layout[k][row][col]
                    except IndexError:
                        pass
        return new_layout

    def pretty_layouts(self):
        newline = '\n'
        return '{\n' + [''.join(
            f"    '{k}': [\n" + f"{''.join([f'        {repr(row)},{newline}' for row in self.layouts[k]])}" +
            '    ],\n' for k in self.layouts
        )][0] + '}\n'

    def update_highlight(self, x, y) -> None:
        pos = self.get_coordinates(x, y)
        if self.not_a_key(pos):
            self.highlight.opacity = 0
        else:
            self.highlight.opacity = self.manager.highlight_color[3]
            self.highlight.position = self.get_position(pos)

    def on_mouse_press(self, x, y, buttons, _modifiers) -> None:
        if buttons & (mouse.LEFT | mouse.RIGHT):
            pos = self.get_coordinates(x, y)
            if self.not_a_key(pos):
                return
            self.deselect_key()  # just in case we had something previously selected
            self.select_key(pos)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self.update_highlight(x + dx, y + dy)

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
                path_name = key_name.split(':')[0]
                layout_path = path_name.split('/')
                layout_name = layout_path[0]
                for name in key_name, path_name, layout_name:
                    if name in self.manager.preview_keys:
                        name, layout = layout_name, (layout_path[1] if len(layout_path) > 1 else '')
                        index, keyboard = self.manager.get_keyboard(name)
                        if layout in keyboard.layouts:
                            keyboard.current_layout = layout
                        self.manager.switch_to(index)
                        return
                if key_name in self.preview_keys:
                    layout = key_name.split(':')[0]
                    if layout in self.layouts:
                        self.current_layout = layout
                    self.update_layout()
                    return
                elif key_name == self.backspace_key:
                    if len(self.manager.image_history) == 0:
                        return
                    if buttons & mouse.LEFT:
                        self.manager.image_buffer, self.manager.next_key_position = self.manager.image_history.pop()
                    elif buttons & mouse.RIGHT:
                        self.manager.image_buffer, self.manager.next_key_position = self.manager.image_history[0]
                        self.manager.image_history.clear()
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
                self.board_sprites[pos[0]][pos[1]].opacity = self.manager.key_color[3]
                self.board_sprites[selected[0]][selected[1]].opacity = 0
            swapped_key = self.layouts[self.current_layout][pos[0]][pos[1]]
            self.layouts[self.current_layout][pos[0]][pos[1]] = \
                self.layouts[self.current_layout][selected[0]][selected[1]]
            self.layouts[self.current_layout][selected[0]][selected[1]] = swapped_key

            # print(self.pretty_layout())
            layout_edit = open(f'keyboards/{self.name}_edit.py', 'w')
            layout_edit.write(f'layouts = {self.pretty_layouts()}')
            layout_edit.close()

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol == key.R:
            if modifiers & key.MOD_SHIFT:
                self.manager.clear_edits()
            if modifiers & key.MOD_ACCEL:  # CMD on OSX, CTRL otherwise
                self.manager.__init__()
        if symbol == key.B:
            if modifiers & key.MOD_SHIFT and modifiers & key.MOD_ACCEL:
                self.manager.output_mode = 'regular'
            elif modifiers & key.MOD_SHIFT:
                self.manager.output_mode = 'opaque'
            elif modifiers & key.MOD_ACCEL:
                self.manager.output_mode = 'transparent'
            if modifiers & (key.MOD_SHIFT | key.MOD_ACCEL):
                self.update_image()
