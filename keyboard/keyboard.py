from io import BytesIO
from itertools import product
from os.path import abspath, relpath, splitext
from typing import Optional, Union

import win32clipboard as clp
from PIL import Image
from cocos.batch import BatchNode
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.sprite import Sprite
from pyglet.image import load
from pyglet.window import key, mouse

import pyperclip
from .key import Key
from .manager import manager, EDIT_VARS


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
        self.mapping = dict()
        self.map_layouts()
        self.preprocess = getattr(module, 'preprocess', manager.preprocess)
        self.postprocess = getattr(module, 'postprocess', manager.postprocess)
        self.window_width = self.board_width \
            * (manager.key_size + manager.key_spacing) \
            + manager.border_width * 2
        self.window_height = (self.board_height + self.screen_height) \
            * (manager.key_size + manager.key_spacing) \
            + manager.border_width * 2
        super().__init__(*manager.app_color, self.window_width, self.window_height)
        self.pressed_key_position = None
        self.current_key_position = None
        self.current_key_is_pressed = False
        self.board_sprites = list()
        self.key_sprites = list()
        self.board = BatchNode()
        self.screen = Key(
            'cell',
            color=manager.screen_color[:3],
            opacity=manager.screen_color[3],
            position=(
                (self.window_width / 2),
                (self.board_height + self.screen_height / 2)
                * (manager.key_size + manager.key_spacing)
                + manager.border_width
            )
        )
        self.screen.resize(
            (manager.key_size + manager.key_spacing) * self.screen_height,
            (self.window_width - manager.border_width * 2)
        )
        self.highlight = Key(
            'cell',
            size=manager.key_size,
            color=manager.highlight_color[:3],
            opacity=0,
        )
        self.pressed_key_back = Key(
            'cell',
            size=manager.key_size * manager.pressed_key_scale,
            color=manager.pressed_key_color[:3],
            opacity=0,
        )
        self.cursor = Key(
            'cursor',
            size=manager.char_size,
            color=manager.cursor_color[:3],
            opacity=manager.cursor_color[3],
            position=(manager.border_width, self.window_height - manager.border_width),
        )
        self.cursor.image_anchor = 0, self.cursor.image.height
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
            self.board_sprites = [[Key('cell', size=manager.key_size) for _ in range(self.board_width)]
                                  for _ in range(self.board_height)]
            self.key_sprites = [[Key() for _ in range(self.board_width)] for _ in range(self.board_height)]

        for row, col in product(range(self.board_height), range(self.board_width)):

            self.board_sprites[row][col].position = self.get_screen_position((row, col))
            self.board_sprites[row][col].color = manager.key_color[:3]
            self.board_sprites[row][col].opacity = manager.key_color[3]
            self.board.add(self.board_sprites[row][col])

        self.current_layout = self.default_layout
        self.loaded = True

    def update_layout(self) -> None:
        """
        Updates the layout on screen according to the ``self.layouts`` variable.
        """
        key_preprocess = self.preprocess if manager.preprocess_keys else lambda x: x
        max_size = max(manager.key_size, manager.char_size)
        for row, col in product(range(self.board_height), range(self.board_width)):
            if self.key_sprites[row][col].parent == self.keys:
                self.keys.remove(self.key_sprites[row][col])
            old_name = self.layouts[self.current_layout][row][col]
            if type(old_name) is str:
                path_name = old_name.split(':', 1)[0]
                layout_name = path_name.split('/', 1)[0]
                for name in old_name, path_name, layout_name:
                    if name in manager.preview_keys:
                        _, keyboard = manager.get_keyboard(layout_name)
                        asset_folder = keyboard.asset_folder if keyboard is not None else self.asset_folder
                        new_name = manager.preview_keys[name]
                        break
                else:
                    asset_folder = self.asset_folder
                    new_name = self.preview_keys[old_name] if old_name in self.preview_keys else old_name
            else:
                asset_folder = self.asset_folder
                new_name = old_name
            self.key_sprites[row][col].rename(old_name)
            self.current_key_position = (row, col)
            self.current_key_is_pressed = False
            new_sprite = Key(new_name, asset_folder, size=max_size, preprocess=key_preprocess)
            new_sprite.rename(old_name)
            new_sprite.position = self.get_screen_position(self.current_key_position)
            new_sprite.resize(manager.key_size)
            self.board_sprites[row][col].opacity = 0 if new_sprite.is_empty() else manager.key_color[3]
            self.key_sprites[row][col] = new_sprite
            self.keys.add(self.key_sprites[row][col])
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
        col = round((x - self.window_width / 2) / (manager.key_size + manager.key_spacing)
                    + (self.board_width - 1) / 2)
        row = round((self.board_height - self.screen_height - 1) / 2
                    - (y - self.window_height / 2) / (manager.key_size + manager.key_spacing))
        if self.not_on_board((row, col)):
            return None
        if precise:
            x2, y2 = self.get_screen_position((row, col))
            if abs(x - x2) > manager.key_size / 2 or abs(y - y2) > manager.key_size / 2:
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
            * (manager.key_size + manager.key_spacing) + self.window_width / 2
        y = ((self.board_height - self.screen_height - 1) / 2 - row) \
            * (manager.key_size + manager.key_spacing) + self.window_height / 2
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

    @property
    def current_key(self) -> Key:
        return self.get_key(self.current_key_position)

    @property
    def current_row(self) -> int:
        return self.current_key_position[0]

    @property
    def current_col(self) -> int:
        return self.current_key_position[1]

    def select_key(self, pos: tuple[int, int]) -> None:
        if self.not_a_key(pos):
            return  # we shouldn't select a nonexistent key
        if pos == self.pressed_key_position:
            return  # key already selected, nothing else to do

        # set selection properties for the selected key
        self.pressed_key_position = pos
        self.pressed_key_back.opacity = manager.pressed_key_color[3]
        self.pressed_key_back.position = self.get_screen_position(pos)

        # move the key to active key node (to be displayed on top of everything else)
        key_sprite = self.get_key(self.pressed_key_position)
        self.keys.remove(key_sprite)
        self.active_key.add(key_sprite)
        key_sprite.resize(manager.key_size * manager.pressed_key_scale)

    def deselect_key(self) -> None:
        self.pressed_key_back.opacity = 0

        if self.nothing_selected():
            return

        # move the key to general key node
        key_sprite = self.get_key(self.pressed_key_position)
        key_sprite.resize(manager.key_size)
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
        pressed_key = self.get_key(pos)
        if pressed_key.name == self.enter_key:
            key_image = Key().base_image
        else:
            key_image = pressed_key.base_image
        key_image = key_image.resize((round(manager.char_size * key_image.width / key_image.height), manager.char_size))
        key_image.format = 'PNG'
        key_image = self.preprocess(key_image)
        if key_image is None:
            manager.image_buffer, manager.next_key_position = manager.image_history.pop()
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
            if pressed_key.name != self.enter_key:
                manager.next_key_position[0] += key_image.width
        self.update_image()

    def clear_screen(self) -> None:
        """
        Clears the screen and clipboard.
        """
        if manager.screen_image is not None and manager.screen_image.parent == self:
            self.remove(manager.screen_image)
        manager.screen_image = None
        self.cursor.position = (manager.border_width, self.window_height - manager.border_width)
        self.cursor.resize(manager.char_size)
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
        (post_processed_image if manager.postprocess_screen else manager.image_buffer).save(data_buffer, format='png')
        data_buffer.seek(0)

        screen_image = load('temp.png', file=data_buffer)
        if manager.screen_image is not None and manager.screen_image.parent == self:
            self.remove(manager.screen_image)
        manager.screen_image = Sprite(
            image=screen_image,
            position=(
                manager.border_width,
                self.window_height - manager.border_width
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
            manager.border_width + manager.next_key_position[0] * manager.screen_image.scale,
            self.window_height - manager.border_width
            - manager.next_key_position[1] * manager.screen_image.scale
        )
        self.cursor.resize(manager.char_size * manager.screen_image.scale)

        background_image = Image.new(
            mode='RGBA',
            size=(post_processed_image.width, post_processed_image.height),
            color=manager.image_color  # for anyone who can't use transparency for some weird tech-related reason
        )
        background_image.alpha_composite(post_processed_image)
        opaque_image = background_image.copy()
        opaque_image.mode = 'RGB'

        path = 'regular.png'
        background_image.save(path)   # in case my clipboard shenanigans don't work, use the file itself

        path = 'opaque.png'
        opaque_image.save(path)   # or use this file if you're having transparency issues

        path = 'transparent.png'
        post_processed_image.save(path)  # or this one if you want to edit in a background or something

        copy_path = abspath(f'{manager.output_mode}.png').encode('utf-16-le') + b'\0'
        copy_file = open(f'{manager.output_mode}.png', 'rb')

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
            newline = '\n'
            return f'{name} = {{\n' + [''.join(
                f"    '{k}': [\n" + f"{''.join([f'        {repr(row)},{newline}' for row in data[k]])}" +
                '    ],\n' for k in data
            )][0] + '}\n'
        else:
            return f'{name} = {data}\n'

    def save_layout(self) -> None:
        self.map_layouts()
        layout_edit = open(f'keyboards/{self.name}_edit.py', 'w')
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
        pos = self.get_layout_position(x, y)
        if self.not_a_key(pos):
            self.highlight.opacity = 0
        else:
            self.highlight.opacity = manager.highlight_color[3]
            self.highlight.position = self.get_screen_position(pos)

    def on_mouse_press(self, x, y, buttons, _modifiers) -> None:
        if buttons & (mouse.LEFT | mouse.RIGHT):
            pos = self.get_layout_position(x, y)
            if self.not_a_key(pos):
                return
            self.deselect_key()  # just in case we had something previously selected
            self.select_key(pos)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self.update_highlight(x, y)

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers) -> None:
        self.on_mouse_motion(x, y, dx, dy)  # move the highlight as well!

    def on_mouse_release(self, x, y, buttons, modifiers) -> None:
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
                path_name = key_name.split(':', 1)[0]
                layout_path = path_name.split('/', 1)
                layout_name = layout_path[0]
                for name in key_name, path_name, layout_name:
                    if name in manager.preview_keys:
                        name, layout = layout_name, (layout_path[1] if len(layout_path) > 1 else '')
                        index, keyboard = manager.get_keyboard(name)
                        if layout in keyboard.layouts:
                            keyboard.current_layout = layout
                        manager.switch_to(index)
                        return
                if key_name in self.preview_keys:
                    layout = key_name.split(':', 1)[0]
                    if layout in self.layouts:
                        self.current_layout = layout
                    self.update_layout()
                    return
                elif key_name == self.backspace_key:
                    if len(manager.image_history) == 0:
                        return
                    if buttons & mouse.LEFT and not modifiers & key.MOD_SHIFT:
                        manager.image_buffer, manager.next_key_position = manager.image_history.pop()
                    elif buttons & mouse.RIGHT or (buttons & mouse.LEFT and modifiers & key.MOD_SHIFT):
                        manager.image_buffer, manager.next_key_position = manager.image_history[0]
                        manager.image_history.clear()
                    self.update_image()
                else:
                    self.press_key(current_pos)
                return
            if self.not_on_board(current_pos):
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
                self.board_sprites[current_pos[0]][current_pos[1]].opacity = manager.key_color[3]
                self.board_sprites[pressed_pos[0]][pressed_pos[1]].opacity = 0
            for d in self.layouts, self.keymap:
                if self.current_layout in d:
                    swapped_key = d[self.current_layout][current_pos[0]][current_pos[1]]
                    d[self.current_layout][current_pos[0]][current_pos[1]] = \
                        d[self.current_layout][pressed_pos[0]][pressed_pos[1]]
                    d[self.current_layout][pressed_pos[0]][pressed_pos[1]] = swapped_key
            self.save_layout()

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol == key.R:
            if modifiers & key.MOD_SHIFT:
                manager.clear_edits()
            if modifiers & key.MOD_ACCEL:  # CMD on OSX, CTRL otherwise
                manager.reload()
            if modifiers & (key.MOD_SHIFT | key.MOD_ACCEL):
                return
        if symbol == key.B:
            if modifiers & key.MOD_SHIFT and modifiers & key.MOD_ACCEL:
                manager.output_mode = 'regular'
            elif modifiers & key.MOD_SHIFT:
                manager.output_mode = 'opaque'
            elif modifiers & key.MOD_ACCEL:
                manager.output_mode = 'transparent'
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
        asset_root = f'keyboards/assets/{self.asset_folder}'
        for path in paths:
            self.layouts[self.current_layout][pos[0]][pos[1]] = splitext(relpath(path, asset_root))[0]
            if self.current_layout in self.keymap:
                self.keymap[self.current_layout][pos[0]][pos[1]] = ''
            pos = self.find_empty(pos)
            if pos is None:
                break
        self.save_layout()
        self.update_layout()

    def on_mouse_enter(self, x, y):
        self.highlight.opacity = manager.highlight_color[3]

    def on_mouse_leave(self, x, y):
        self.highlight.opacity = 0
