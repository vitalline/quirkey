from io import BytesIO
from itertools import product
from math import lcm
from os.path import abspath, relpath, splitext
from typing import Optional, Union

import win32clipboard as clp
from PIL import Image
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.rect import Rect
from cocos.sprite import Sprite
from pyglet.image import load
from pyglet.window import key, mouse

import pyperclip
from .key import Key
from .manager import manager, OutputMode, EDIT_VARS


class Keyboard(ColorLayer):
    """
    A ``ColorLayer`` that draws a keyboard on screen.
    """

    def __init__(self, name, module) -> None:
        """
        Creates a keyboard layer.

        :param name: The keyboard name. Should normally match the module name.
        :param module: The module defining the keyboard.
        """
        # super boring initialization stuff
        self.is_event_handler = True
        self.name = name
        self.board_height = getattr(module, 'board_height', 0)
        self.board_width = getattr(module, 'board_width', 0)
        self.screen_height = getattr(module, 'screen_height', 3)
        self.backspace_key = getattr(module, 'backspace_key', 'backspace')
        self.enter_key = getattr(module, 'enter_key', 'enter')
        self.preview_keys = getattr(module, 'preview_keys', dict())
        self.fixed_layout = getattr(module, 'fixed_layout', False)
        self.asset_folder = getattr(module, 'asset_folder', self.name)
        self.layouts = self.extend_layouts(module.layouts if hasattr(module, 'layouts') else {'': [[]]})
        self.default_layout = getattr(module, 'default_layout', sorted(self.layouts.keys())[0])
        self.keymap = getattr(module, 'keymap', dict())
        self.alt_text = getattr(module, 'alt_text', dict())
        self.mapping = dict()
        self.map_layouts()
        self.key_size_value = getattr(module, 'key_size', None)
        self.char_size_value = getattr(module, 'char_size', None)
        self.key_size, self.char_size = self.key_size_value, self.char_size_value
        # If neither size value is set to a valid size, use the values provided by keyboard manager
        if not self.key_size_value and not self.char_size_value:
            self.key_size, self.char_size = manager.key_size, manager.char_size
        elif self.key_size_value < 0 and self.char_size_value < 0:
            self.key_size, self.char_size = manager.key_size, manager.char_size
        # If one value is explicitly set to 0, use the value provided by keyboard manager (or default to 64)
        elif self.key_size_value == 0:
            self.key_size = manager.key_size
        elif self.char_size_value == 0:
            self.char_size = manager.char_size
        # Otherwise, if one value isn't set (or is invalid), use the other value (same as in manager, but per keyboard)
        elif not self.key_size_value or self.key_size_value < 0:
            self.key_size = self.char_size
        elif not self.char_size_value or self.char_size_value < 0:
            self.char_size = self.key_size
        # Apply size multipliers (if any exist and are valid)
        self.size_multiplier = getattr(module, 'size_multiplier', 1)
        self.key_size_multiplier = getattr(module, 'key_size_multiplier', self.size_multiplier)
        self.char_size_multiplier = getattr(module, 'char_size_multiplier', self.size_multiplier)
        if self.key_size_multiplier > 0:
            self.key_size = round(self.key_size * self.key_size_multiplier)
        if self.char_size_multiplier > 0:
            self.char_size = round(self.char_size * self.char_size_multiplier)
        self.key_spacing = getattr(module, 'key_spacing', manager.key_spacing)
        self.border_width = getattr(module, 'border_width', manager.border_width)
        self.app_color = getattr(module, 'app_color', manager.app_color)
        self.image_color = getattr(module, 'image_color', manager.image_color)
        self.key_color = getattr(module, 'key_color', manager.key_color)
        self.screen_color = getattr(module, 'screen_color', manager.screen_color)
        self.highlight_color = getattr(module, 'highlight_color', manager.highlight_color)
        self.pressed_key_color = getattr(module, 'pressed_key_color', manager.pressed_key_color)
        self.pressed_key_scale = getattr(module, 'pressed_key_scale', manager.pressed_key_scale)
        self.cursor_color = getattr(module, 'cursor_color', manager.cursor_color)
        self.resample_value = getattr(module, 'resample', manager.resample_value)
        # If resample value is -1, store that info for future reference and use a resample of 0
        self.resample = self.resample_value
        self.use_old_nearest = self.resample_value == -1
        if self.use_old_nearest:
            self.resample = 0
        self.preprocess = getattr(module, 'preprocess', manager.preprocess)
        self.postprocess = getattr(module, 'postprocess', manager.postprocess)
        self.preprocess_keys = getattr(module, 'preprocess_keys', manager.preprocess_keys)
        self.postprocess_screen = getattr(module, 'postprocess_screen', manager.postprocess_screen)
        self.window_width = self.board_width \
            * (self.key_size + self.key_spacing) \
            + self.border_width * 2
        self.window_height = (self.board_height + self.screen_height) \
            * (self.key_size + self.key_spacing) \
            + self.border_width * 2
        super().__init__(*self.app_color, self.window_width, self.window_height)
        self.pressed_key_position = None
        self.current_key_position = None
        self.current_key_is_pressed = False
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.screen = Key(
            'cell',
            color=self.screen_color[:3],
            opacity=self.screen_color[3],
            position=(
                (self.window_width / 2),
                (self.board_height + self.screen_height / 2)
                * (self.key_size + self.key_spacing)
                + self.border_width
            )
        )
        self.screen.resize(
            (self.key_size + self.key_spacing) * self.screen_height,
            (self.window_width - self.border_width * 2)
        )
        self.screen_bounds = self.screen.get_AABB()
        self.highlight = Key(
            'cell',
            size=self.key_size,
            color=self.highlight_color[:3],
            opacity=0,
        )
        self.pressed_key_back = Key(
            'cell',
            size=self.key_size * self.pressed_key_scale,
            color=self.pressed_key_color[:3],
            opacity=0,
        )
        self.cursor = Key(
            'cursor',
            size=self.char_size,
            color=self.cursor_color[:3],
            opacity=self.cursor_color[3],
            position=(self.border_width, self.window_height - self.border_width),
        )
        self.cursor.image_anchor = 0, self.cursor.image.height
        self.cursor.resize(min(self.char_size, self.screen.height))
        self.keys = BatchNode()
        self.overlay = BatchNode()
        self.active_key = BatchNode()
        self.add(self.board, z=1)
        self.add(self.highlight, z=2)
        self.add(self.keys, z=3)
        self.add(self.overlay, z=4)
        self.add(self.active_key, z=5)
        self.board.add(self.screen)
        self.overlay.add(self.pressed_key_back)
        self.overlay.add(self.cursor)

        for row in range(self.board_height):
            self.board_sprites = [
                [Key('cell', size=self.key_size) for _ in range(self.board_width)]
                for _ in range(self.board_height)
            ]
            self.key_sprites = [[Key() for _ in range(self.board_width)] for _ in range(self.board_height)]

        for row, col in product(range(self.board_height), range(self.board_width)):
            self.board_sprites[row][col].position = self.get_screen_position((row, col))
            self.board_sprites[row][col].color = self.key_color[:3]
            self.board_sprites[row][col].opacity = self.key_color[3]
            self.board.add(self.board_sprites[row][col])

        self.current_layout = self.default_layout
        self.loaded = True

    def update_layout(self) -> None:
        """
        Updates the layout on screen according to the ``self.layouts`` variable.
        """
        key_preprocess = self.preprocess if self.preprocess_keys else lambda x: x
        if self.resample == 0 and not self.use_old_nearest:
            max_size = lcm(self.key_size, self.char_size)
        else:
            max_size = max(self.key_size * self.pressed_key_scale, self.char_size)
        for row, col in product(range(self.board_height), range(self.board_width)):
            if self.key_sprites[row][col].parent == self.keys:
                self.keys.remove(self.key_sprites[row][col])
            old_name = self.layouts[self.current_layout][row][col]
            asset_folder = self.asset_folder
            new_name = old_name
            if type(old_name) is str:
                if old_name[:1] == '/':
                    key_name = old_name[1:]
                    layout_name = key_name.split(':', 1)[0]
                    keyboard_name = layout_name.split('/', 1)[0]
                    for name in key_name, layout_name, keyboard_name:
                        if name in manager.preview_keys:
                            _, keyboard = manager.get_keyboard(keyboard_name)
                            asset_folder = keyboard.asset_folder if keyboard is not None else self.asset_folder
                            new_name = manager.preview_keys[name]
                            break
                if old_name[:2] == '~/':
                    key_name = old_name[2:]
                    layout_name = key_name.split(':', 1)[0]
                    for name in key_name, layout_name:
                        if name in self.preview_keys:
                            new_name = self.preview_keys[name]
                            break
            self.key_sprites[row][col].rename(old_name)
            self.current_key_position = (row, col)
            self.current_key_is_pressed = False
            new_sprite = Key(new_name, asset_folder, size=max_size, preprocess=key_preprocess, resample=self.resample)
            new_sprite.rename(old_name)
            new_sprite.position = self.get_screen_position(self.current_key_position)
            new_sprite.resize(self.key_size)
            self.board_sprites[row][col].opacity = 0 if new_sprite.is_empty() else self.key_color[3]
            self.key_sprites[row][col] = new_sprite
            self.keys.add(self.key_sprites[row][col])
        director.window.set_caption(f'Keyboard: {self.name}/{self.current_layout}')
        self.loaded = True

    @property
    def is_loaded(self) -> bool:
        """
        Check if the keyboard is fully initialized and loaded into memory.

        :return: True if the keyboard has been loaded, False otherwise.
        """
        return hasattr(self, 'loaded') and self.loaded

    def get_layout_position(self, x: float, y: float, precise: bool = True) -> Optional[tuple[int, int]]:
        """
        Convert mouse event (screen) coordinates to layout coordinates, starting from the upper left corner.

        Note that the row index is returned first, for more intuitive layout notation.

        :param x: The x coordinate of the mouse event.
        :param y: The y coordinate of the mouse event.
        :param precise: If True, points between the key spaces return None.
                        If False, coordinates of the closest key space are returned instead.
                        Default: True.
        :return: A tuple of (row, col) layout coordinates, or None if the coordinates are out of bounds.
        """
        x, y = director.get_virtual_coordinates(x, y)
        col = round((x - self.window_width / 2) / (self.key_size + self.key_spacing)
                    + (self.board_width - 1) / 2)
        row = round((self.board_height - self.screen_height - 1) / 2
                    - (y - self.window_height / 2) / (self.key_size + self.key_spacing))
        if self.not_on_board((row, col)):
            return None
        if precise:
            x2, y2 = self.get_screen_position((row, col))
            if abs(x - x2) > self.key_size / 2 or abs(y - y2) > self.key_size / 2:
                return None
        return row, col

    def get_screen_position(self, pos: tuple[int, int]) -> tuple[float, float]:
        """
        Convert layout coordinates to screen coordinates (i.e. for positioning keys on the screen).

        Note that the row index should be first in the tuple, for more intuitive layout notation.

        :param pos: A tuple of (row, col) layout coordinates.
        :return: A tuple of (x, y) mouse event coordinates.
        """
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
        return self.not_a_key(self.pressed_key_position)

    @staticmethod
    def is_inside(pos: tuple[int, int], box: Rect) -> bool:
        return (
                box.left <= pos[0] < box.right and
                box.bottom <= pos[1] < box.top
        )

    @property
    def current_key(self) -> Key:
        return self.get_key(self.current_key_position)

    @property
    def current_row(self) -> int:
        return self.current_key_position[0]

    @property
    def current_col(self) -> int:
        return self.current_key_position[1]

    def get_alt_text(self, pos: tuple[int, int]) -> str:
        try:
            return self.alt_text[self.current_layout][pos[0]][pos[1]]
        except (IndexError, KeyError):
            return ''

    def add_alt_text(self, pos: tuple[int, int]) -> None:
        text_buffer = manager.text_buffer
        alt_text = self.get_alt_text(pos)
        if len(alt_text) > 1 and alt_text[0].isalnum() and (len(text_buffer) > 0 and not text_buffer[-1].isspace()):
            text_buffer += ' '
        manager.text_buffer = text_buffer + alt_text

    def select_key(self, pos: tuple[int, int]) -> None:
        if self.not_a_key(pos):
            return  # we shouldn't select a nonexistent key
        if pos == self.pressed_key_position:
            return  # key already selected, nothing else to do

        # set selection properties for the selected key
        self.pressed_key_position = pos
        self.pressed_key_back.opacity = self.pressed_key_color[3]
        self.pressed_key_back.position = self.get_screen_position(pos)

        # move the key to active key node (to be displayed on top of everything else)
        key_sprite = self.get_key(self.pressed_key_position)
        self.keys.remove(key_sprite)
        self.active_key.add(key_sprite)
        key_sprite.resize(self.key_size * self.pressed_key_scale)

    def deselect_key(self) -> None:
        self.pressed_key_back.opacity = 0

        if self.nothing_selected():
            return

        # move the key to general key node
        key_sprite = self.get_key(self.pressed_key_position)
        key_sprite.resize(self.key_size)
        self.active_key.remove(key_sprite)
        self.keys.add(key_sprite)

        self.pressed_key_position = None

    def press_key(self, pos: tuple[int, int]) -> None:
        """
        Update ``manager.image_buffer`` according to the key represented by ``pos``.

        Note that the check for keyboard/layout switch keys happens before calling this function,
        so using its coordinates here will simply add its image to the screen.

        :param pos: A tuple of (row, col) layout coordinates.
        """
        manager.image_history.append((manager.image_buffer, manager.next_key_position.copy()))
        manager.text_history.append(manager.text_buffer)
        pressed_key = self.get_key(pos)
        if pressed_key.name == self.enter_key:
            key_image = Key().base_image
        else:
            key_image = pressed_key.base_image
        key_image = key_image.resize(
            (round(self.char_size * key_image.width / key_image.height), self.char_size),
            resample=self.resample
        )
        key_image.format = 'PNG'
        key_image = self.preprocess(key_image)
        if key_image is None:
            manager.image_buffer, manager.next_key_position = manager.image_history.pop()
            manager.text_buffer = manager.text_history.pop()
        else:
            if pressed_key.name == self.enter_key:
                manager.next_key_position = [0, manager.next_key_position[1] + key_image.height]
            if manager.image_buffer is None:
                new_buffer = Image.new(
                    mode='RGBA',
                    size=(manager.next_key_position[0] + key_image.width,
                          manager.next_key_position[1] + key_image.height),
                    color=(0, 0, 0, 0)
                )
            else:
                new_buffer = Image.new(
                    mode='RGBA',
                    size=(max(manager.image_buffer.width, manager.next_key_position[0] + key_image.width),
                          max(manager.image_buffer.height, manager.next_key_position[1] + key_image.height)),
                    color=(0, 0, 0, 0)
                )
                new_buffer.paste(manager.image_buffer)
            # noinspection PyTypeChecker
            new_buffer.paste(key_image, tuple(manager.next_key_position))
            manager.image_buffer = new_buffer
            if pressed_key.name == self.enter_key:
                manager.text_buffer += '\n'
            else:
                self.add_alt_text(pos)
                manager.next_key_position[0] += key_image.width
        self.update_image()

    def clear_screen(self) -> None:
        """
        Clears the screen and clipboard.
        """
        if manager.screen_image is not None and manager.screen_image.parent == self:
            self.remove(manager.screen_image)
        manager.screen_image = None
        self.cursor.position = (self.border_width, self.window_height - self.border_width)
        self.cursor.resize(min(self.char_size, self.screen.height))
        pyperclip.copy('')

    def update_image(self) -> None:
        """
        Updates the image on the screen and the output files to match ``manager.image_buffer``,
        and copies the file in the current output mode to the clipboard if the buffer isn't empty.

        Note that the postprocessing function should be called regardless of whether the buffer is empty.
        """
        if manager.image_buffer is not None:
            manager.image_buffer.format = 'PNG'

        post_processed_image = self.postprocess(manager.image_buffer)
        if post_processed_image is None:
            self.clear_screen()
            return

        data_buffer = BytesIO()
        (post_processed_image if self.postprocess_screen else manager.image_buffer).save(data_buffer, format='png')
        data_buffer.seek(0)

        screen_image = load('temp.png', file=data_buffer)
        if manager.screen_image is not None and manager.screen_image.parent == self:
            self.remove(manager.screen_image)
        manager.screen_image = Sprite(
            image=screen_image,
            position=(
                self.border_width,
                self.window_height - self.border_width
            ),
            anchor=(0, screen_image.height)
        )
        manager.screen_image.scale = min(
            self.screen.width / (manager.screen_image.width + self.cursor.width),
            self.screen.height / manager.screen_image.height,
            1
        )
        self.add(manager.screen_image, z=3)
        self.cursor.position = (
            self.border_width + manager.next_key_position[0] * manager.screen_image.scale,
            self.window_height - self.border_width
            - manager.next_key_position[1] * manager.screen_image.scale
        )
        self.cursor.resize(self.char_size * manager.screen_image.scale)

        background_image = Image.new(
            mode='RGBA',
            size=(post_processed_image.width, post_processed_image.height),
            color=self.image_color  # for anyone who can't use transparency for some weird tech-related reason
        )
        background_image.alpha_composite(post_processed_image)
        opaque_image = background_image.copy()
        opaque_image.mode = 'RGB'

        path = 'image_regular.png'
        background_image.save(path)   # in case my clipboard shenanigans don't work, use the file itself

        path = 'image_opaque.png'
        opaque_image.save(path)   # or use this file if you're having transparency issues

        path = 'image_transparent.png'
        post_processed_image.save(path)  # or this one if you want to edit in a background or something

        copy_path = abspath(f'image_{manager.output_mode.value}.png').encode('utf-16-le') + b'\0'
        copy_file = open(f'image_{manager.output_mode.value}.png', 'rb')

        clp.OpenClipboard()
        clp.EmptyClipboard()  # You may have seen this on https://stackoverflow.com/q/66845295/17391024. You're welcome.
        clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), copy_path)         # works for Discord
        clp.SetClipboardData(clp.RegisterClipboardFormat('image/png'), copy_file.read())  # works for PDN & TG
        clp.CloseClipboard()

    def map_layouts(self) -> None:
        self.mapping = dict()
        for k, v in self.keymap.items():
            for row, line in enumerate(v):
                for col, char in enumerate(line):
                    if k not in self.mapping:
                        self.mapping[k] = dict()
                    keys = char
                    modifier_code = 0
                    if type(keys) == str:
                        key_combos = keys.upper().split(',')
                        for key_combo in key_combos:
                            key_codes = key_combo.strip().split('+')
                            modifiers, key_code = ['MOD_' + code for code in key_codes[:-1]], key_codes[-1]
                            if key_code and key_code[0] in '0123456789':
                                key_code = '_' + key_code
                            if key_code.startswith('MOTION_'):
                                continue  # the "MOTION" key codes shouldn't be used for explicit mapping
                            elif key_code.startswith('MOD_'):
                                continue  # TODO: the "MOD" key codes might be used for explicit mapping, but not yet.
                            else:
                                key_code = getattr(key, key_code, 0)
                            for modifier in modifiers:
                                new_modifier_code = getattr(key, modifier, 0)
                                if type(new_modifier_code) == int:
                                    modifier_code |= new_modifier_code
                            if type(key_code) == int:
                                if key_code not in self.mapping[k]:
                                    self.mapping[k][key_code] = dict()
                                self.mapping[k][key_code][modifier_code] = (row, col)

    def extend_layouts(self, layouts: dict) -> dict:
        if self.board_height == 0:
            self.board_height = max(len(layouts[k]) for k in layouts)
        if self.board_width == 0:
            self.board_width = max(len(row) for k in layouts for row in layouts[k])
        new_layouts = {k: [['' for _ in range(self.board_width)]
                       for _ in range(self.board_height)]
                       for k in layouts.keys()}
        for k in new_layouts.keys():
            for row in range(len(new_layouts[k])):
                for col in range(len(new_layouts[k][row])):
                    try:
                        new_layouts[k][row][col] = layouts[k][row][col]
                    except IndexError:
                        pass
        return new_layouts

    def pretty_print(self, name: str) -> str:
        data = getattr(self, name, None)
        if type(data) == dict:
            if data:
                newline = '\n'
                return f'{name} = {{\n' + [''.join(
                    f"    '{k}': [\n" + f"{''.join([f'        {repr(row)},{newline}' for row in data[k]])}" +
                    '    ],\n' for k in data
                )][0] + '}\n'
            return ''
        else:
            return f'{name} = {data}\n'

    def save_layout(self) -> None:
        self.map_layouts()
        layout_edit = open(f'keyboards/{self.name}_edit.py', 'w', encoding='utf-8')
        for var in EDIT_VARS:
            layout_edit.write(self.pretty_print(var))
        layout_edit.close()

    def find_empty(self, start: tuple[int, int] = (0, 0)) -> Optional[tuple[int, int]]:
        layout = self.layouts[self.current_layout]
        for row in range(start[0], len(layout)):
            for col in range((start[1] if row == start[0] else 0), len(layout[row])):
                if layout[row][col] == '':
                    return row, col
        for row in range(start[0] + 1):
            for col in range(start[1] if row == start[0] else len(layout[row])):
                if layout[row][col] == '':
                    return row, col
        return None

    def update_highlight(self, x, y) -> None:
        # TODO: add alt text preview
        pos = self.get_layout_position(x, y)
        if self.not_a_key(pos):
            self.highlight.opacity = 0
        else:
            self.highlight.opacity = self.highlight_color[3]
            self.highlight.position = self.get_screen_position(pos)

    def on_mouse_press(self, x, y, buttons, _modifiers) -> None:
        if buttons & (mouse.LEFT | mouse.RIGHT):
            self.current_key_is_pressed = False
            pos = self.get_layout_position(x, y)
            if self.not_a_key(pos):
                return
            self.deselect_key()  # just in case we had something previously selected
            self.select_key(pos)

    def on_mouse_motion(self, x, y, _dx, _dy) -> None:
        self.update_highlight(x, y)

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers) -> None:
        self.on_mouse_motion(x, y, dx, dy)  # move the highlight as well!

    def on_mouse_release(self, x, y, buttons, modifiers) -> None:
        if self.is_inside((x, y), self.screen_bounds):
            if buttons & mouse.LEFT:
                self.update_image()
            if buttons & mouse.RIGHT:
                pyperclip.copy(manager.text_buffer)
            return
        if self.nothing_selected():
            return
        if buttons & (mouse.LEFT | mouse.RIGHT):
            current_pos = self.get_layout_position(x, y)
            pressed_pos = self.pressed_key_position
            self.deselect_key()
            self.current_key_position = current_pos
            if current_pos == pressed_pos:
                self.current_key_is_pressed = True
                # TODO: make "key is preview?" into a convenience method (or at least have the data cached somewhere)
                key_name = self.get_key(pressed_pos).name
                if key_name[:1] == '/':
                    key_name = key_name[1:]
                    layout_name = key_name.split(':', 1)[0]
                    layout_path = layout_name.split('/', 1)
                    keyboard_name = layout_path[0]
                    for name in key_name, layout_name, keyboard_name:
                        if name in manager.preview_keys:
                            name, layout = keyboard_name, (layout_path[1] if len(layout_path) > 1 else '')
                            index, keyboard = manager.get_keyboard(name)
                            if layout in keyboard.layouts:
                                keyboard.current_layout = layout
                            manager.switch_to(index)
                            break
                    return
                if key_name[:2] == '~/':
                    key_name = key_name[2:]
                    layout_name = key_name.split(':', 1)[0]
                    if layout_name in self.layouts:
                        self.current_layout = layout_name
                        self.update_layout()
                    return
                if key_name == self.backspace_key:
                    if len(manager.image_history) == 0:
                        return
                    if buttons & mouse.LEFT and not modifiers & key.MOD_SHIFT:
                        manager.image_buffer, manager.next_key_position = manager.image_history.pop()
                        manager.text_buffer = manager.text_history.pop()
                    elif buttons & mouse.RIGHT or (buttons & mouse.LEFT and modifiers & key.MOD_SHIFT):
                        manager.image_buffer, manager.next_key_position = manager.image_history[0]
                        manager.image_history.clear()
                        manager.text_buffer = manager.text_history[0]
                        manager.text_history.clear()
                    self.update_image()
                else:
                    self.press_key(current_pos)
                return
            if current_pos is None or self.not_on_board(current_pos):
                current_pos = pressed_pos  # to avoid dragging a key off the board, place it back on its cell

            if pressed_pos == current_pos or self.fixed_layout:
                return

            key_sprite = self.get_key(pressed_pos)
            key_sprite.position = self.get_screen_position(current_pos)
            swapped_key = self.get_key(current_pos)
            swapped_key.position = self.get_screen_position(pressed_pos)
            self.key_sprites[current_pos[0]][current_pos[1]] = key_sprite
            self.key_sprites[pressed_pos[0]][pressed_pos[1]] = swapped_key
            if swapped_key.is_empty():
                self.board_sprites[current_pos[0]][current_pos[1]].opacity = self.key_color[3]
                self.board_sprites[pressed_pos[0]][pressed_pos[1]].opacity = 0
            for d in self.layouts, self.keymap, self.alt_text:
                if self.current_layout in d:
                    swapped_key = d[self.current_layout][current_pos[0]][current_pos[1]]
                    d[self.current_layout][current_pos[0]][current_pos[1]] = \
                        d[self.current_layout][pressed_pos[0]][pressed_pos[1]]
                    d[self.current_layout][pressed_pos[0]][pressed_pos[1]] = swapped_key
            self.save_layout()

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol == key.T:
            if modifiers & key.MOD_ALT:
                pyperclip.copy(manager.text_buffer)
                return
        if symbol == key.R:
            if modifiers & key.MOD_ALT:
                self.update_image()
                return
            if modifiers & key.MOD_SHIFT:
                manager.clear_edits()
            if modifiers & key.MOD_ACCEL:  # CMD on OSX, CTRL otherwise
                manager.reload()
            if modifiers & (key.MOD_SHIFT | key.MOD_ACCEL):
                return
        if symbol == key.B:
            if modifiers & key.MOD_SHIFT and modifiers & key.MOD_ACCEL:
                manager.output_mode = OutputMode.REGULAR
            elif modifiers & key.MOD_SHIFT:
                manager.output_mode = OutputMode.OPAQUE
            elif modifiers & key.MOD_ACCEL:
                manager.output_mode = OutputMode.TRANSPARENT
            if modifiers & (key.MOD_SHIFT | key.MOD_ACCEL):
                self.update_image()
                return
        if self.current_layout in self.mapping:
            if symbol in self.mapping[self.current_layout]:
                modifier_code = 0
                for k in sorted(self.mapping[self.current_layout][symbol].keys()):
                    if modifiers & k:
                        modifier_code = k
                position = self.mapping[self.current_layout][symbol].get(modifier_code, None)
                if not self.not_a_key(position):
                    x, y = self.get_screen_position(position)
                    self.on_mouse_press(x, y, mouse.LEFT, modifiers)
                    self.on_mouse_release(x, y, mouse.LEFT, modifiers)

    def on_file_drop(self, x, y, paths):
        # TODO: add keycode input
        if self.fixed_layout:
            return
        pos = self.get_layout_position(x, y)
        if pos is None:
            pos = self.find_empty()
            if pos is None:
                return
        root = f'keyboards/assets/{self.asset_folder}'
        for path in paths:
            self.layouts[self.current_layout][pos[0]][pos[1]] = splitext(relpath(path, root))[0].replace('\\', '/')
            for d in self.keymap, self.alt_text:
                if self.current_layout in d:
                    d[self.current_layout][pos[0]][pos[1]] = ''
            pos = self.find_empty(pos)
            if pos is None:
                break
        self.save_layout()
        self.update_layout()

    def on_mouse_enter(self, x, y):
        self.update_highlight(x, y)

    def on_mouse_leave(self, _x, _y):
        self.highlight.opacity = 0
