import os
from configparser import ConfigParser, Error
from enum import Enum
from glob import iglob
from importlib import import_module, invalidate_caches, reload
from traceback import print_exc
from typing import Callable, Optional, TypeVar, TYPE_CHECKING

from PIL import Image
from PIL.ImageColor import getrgb
from cocos.cocosnode import CocosNode
from cocos.director import director
from cocos.scene import Scene

if TYPE_CHECKING:
    from keyboard.keyboard import Keyboard

EDIT_VARS = ('layouts', 'keymap', 'alt_text')


class OutputMode(Enum):
    REGULAR = 'regular'
    OPAQUE = 'opaque'
    TRANSPARENT = 'transparent'


class KeyboardManager(CocosNode):
    """
    Class that creates and handles the main window and manages the keyboard layers.

    You should not directly instantiate the class, instead you do::

        from keyboard import manager

    to access the only KeyboardManager instance.
    """

    def __init__(self) -> None:
        if self.is_loaded:
            invalidate_caches()
            director.window.set_caption('Loading...')
            director.window.set_size(0, 0)
            self.remove(self.keyboards[self.keyboard_index])
        else:
            self.loaded = False
            director.init(width=0, height=0, caption='Loading...', autoscale=False, file_drops=True)
            super().__init__()
            director.window.remove_handlers(director._default_event_handler)
        self.screen_image = None
        self.image_buffer = None
        self.image_history = []
        self.text_buffer = ''
        self.text_history = []
        self.next_key_position = [0, 0]
        self.config = ConfigParser()
        self.config.read('config.ini')
        try:
            self.load_order = self.config.get('Keyboard Settings', 'load_order').split(',')
        except Error:
            self.load_order = [name[10:-3] for name in iglob('keyboards/*.py')]
        self.load_order = [name.strip() for name in self.load_order]
        self.key_size_value = self.load_value('key_size', 0)
        self.char_size_value = self.load_value('char_size', 0)
        self.key_size, self.char_size = self.key_size_value, self.char_size_value
        # If neither size value is set to a valid size, use a default size of 64
        if self.key_size_value <= 0 and self.char_size_value <= 0:
            self.key_size, self.char_size = 64, 64
        # If one value isn't set to a valid size, use the other value instead
        elif self.key_size_value <= 0:
            self.key_size = self.char_size
        elif self.char_size_value <= 0:
            self.char_size = self.key_size
        self.key_spacing = self.load_value('key_spacing', 4)
        self.border_width = self.load_value('border_width', 16)
        self.app_color = self.load_value('app_color', (34, 34, 34))
        self.image_color = self.load_value('image_color', (34, 34, 34, 0))
        self.key_color = self.load_value('key_color', (51, 51, 51))
        self.screen_color = self.load_value('screen_color', (51, 51, 51))
        self.highlight_color = self.load_value('highlight_color', (255, 255, 255, 51))
        self.pressed_key_color = self.load_value('pressed_key_color', (102, 102, 102))
        self.pressed_key_scale = self.load_value('pressed_key_scale', 1.25)
        self.cursor_color = self.load_value('cursor_color', (255, 255, 255, 51))
        self.resample_value = self.load_value('resample', Image.BILINEAR)
        self.resample = self.resample_value
        # If resample value is -1, store that info for future reference and use a resample of 0
        self.use_old_nearest = self.resample_value == -1
        if self.use_old_nearest:
            self.resample = 0
        if not self.is_loaded:
            self.preprocess_modules, self.postprocess_modules, self.preprocess = dict(), dict(), lambda x: x
            self.keyboard_modules, self.keyboard_edit_modules, self.postprocess = dict(), dict(), lambda x: x
        self.preprocess_keys = self.load_value('preprocess_keys', False)
        self.postprocess_screen = self.load_value('postprocess_screen', True)
        self.output_mode = OutputMode.REGULAR
        self.keyboards = []
        self.keyboard_index = 0
        self.keyboard_dict = {}
        self.current_keyboard = None
        self.preview_keys = dict()

    def init_modules(self) -> None:
        """
        Initializes or reinitializes the keyboard and effect modules.
        """
        preprocess_names = self.load_value('preprocess', '').split(',')
        preprocess_names = [name.strip() for name in preprocess_names]
        self.preprocess_modules, self.preprocess = self.load_processing(preprocess_names, self.preprocess_modules)
        postprocess_names = self.load_value('postprocess', '').split(',')
        postprocess_names = [name.strip() for name in postprocess_names]
        self.postprocess_modules, self.postprocess = self.load_processing(postprocess_names, self.postprocess_modules)
        from .keyboard import Keyboard
        for name in self.load_order:
            for module_dict, import_string in ((self.keyboard_modules, 'keyboards.{}'),
                                               (self.keyboard_edit_modules, 'keyboards.{}_edit')):
                try:
                    if self.is_loaded and name in module_dict:
                        module_dict[name] = reload(module_dict[name])
                    else:
                        module_dict[name] = import_module(import_string.format(name))
                except ModuleNotFoundError:
                    pass
            if os.path.isfile(f'keyboards/{name}_edit.py'):
                for var in EDIT_VARS:
                    if hasattr(self.keyboard_edit_modules[name], var):
                        setattr(self.keyboard_modules[name], var, getattr(self.keyboard_edit_modules[name], var))
        self.keyboards = [Keyboard(name, self.keyboard_modules[name]) for name in self.load_order]
        self.add(self.keyboards[self.keyboard_index])
        self.keyboard_dict = {keyboard.name: (i, keyboard) for i, keyboard in enumerate(self.keyboards)}
        self.keyboard_dict[None] = (-1, None)
        self.load_preview_keys()
        for keyboard in self.keyboards:
            self.current_keyboard = keyboard
            keyboard.update_layout()
        self.keyboard_index = 0
        self.current_keyboard = self.keyboards[self.keyboard_index]
        self.current_keyboard.update_image()
        director.window.set_size(self.keyboards[self.keyboard_index].window_width,
                                 self.keyboards[self.keyboard_index].window_height)
        director.window.set_caption(f'Keyboard: /{self.current_keyboard.name}/{self.current_keyboard.current_layout}')
        self.loaded = True

    @property
    def is_loaded(self) -> bool:
        """
        Check if the window and all its modules are fully initialized.

        :return: True if the application has loaded, False otherwise.
        """
        return hasattr(self, 'loaded') and self.loaded

    def reload(self) -> None:
        """
        Reloads the manager and all its modules.
        """
        highlight_position = self.keyboards[self.keyboard_index].highlight.position
        self.__init__()
        self.init_modules()
        self.current_keyboard.update_highlight(*highlight_position)

    T = TypeVar('T')

    def load_value(self, k: str, default: T) -> T:
        """
        Loads a setting value from the main configuration file, or ``default`` if the setting doesn't exist.

        :param k: The setting key.
        :param default: Value to default to if the setting doesn't exist.
        :return: The requested value.
        """
        if type(default) == bool:
            value = self.config.getboolean('Keyboard Settings', k, fallback=default)
        else:
            value = self.config.get('Keyboard Settings', k, fallback=default)
        if type(default) == tuple and len(default) in (3, 4):
            if value == default:
                color_tuple = default
            else:
                color_tuple = getrgb(value)  # we just kinda *assume* this is a color
            color_tuple = (*color_tuple[:3], (color_tuple[3] if len(color_tuple) == 4 else 255))
            return color_tuple
        else:
            return type(default)(value)

    def load_processing(
            self, processing_list: list[str], processing_modules: dict
    ) -> tuple[dict, Callable[[Optional[Image.Image]], Optional[Image.Image]]]:

        for name in processing_list:
            try:
                if self.is_loaded and name in processing_modules:
                    processing_modules[name] = reload(processing_modules[name])
                else:
                    processing_modules[name] = import_module(f'effects.{name}')
            except ModuleNotFoundError:
                pass

        def processing_func(image: Optional[Image.Image]) -> Optional[Image.Image]:
            for i in processing_list:
                if image is not None:
                    image.format = 'PNG'
                try:
                    image = getattr(processing_modules.get(i, None), 'process', lambda x: x)(image)
                except Exception:
                    print_exc()
            return image

        return processing_modules, processing_func

    def load_preview_keys(self) -> None:
        for keyboard in self.keyboards:
            default_preview = keyboard.preview_keys.get('default', None)
            for k in keyboard.preview_keys:
                if k != 'default':
                    self.preview_keys[f'{keyboard.name}/{k}'] = keyboard.preview_keys[k]
            for k in keyboard.layouts:
                if f'{keyboard.name}/{k}' not in self.preview_keys:
                    self.preview_keys[f'{keyboard.name}/{k}'] = default_preview
            if f'{keyboard.name}' not in self.preview_keys:
                self.preview_keys[f'{keyboard.name}'] = default_preview

    @property
    def keyboard(self) -> 'Keyboard':
        return self.current_keyboard

    def get_keyboard(self, name: str = '') -> Optional[int]:
        return self.keyboard_dict.get(name, self.keyboard_dict[None])

    def run(self):
        director.run(Scene(self))

    def clear_edits(self):
        for keyboard in self.keyboards:
            edit_path = f'keyboards/{keyboard.name}_edit.py'
            if os.path.isfile(edit_path):
                os.remove(edit_path)

    def switch_to(self, index: int):
        if self.screen_image is not None \
                and self.screen_image.parent == self.keyboards[self.keyboard_index] \
                and self.keyboard_index != index:
            self.keyboards[self.keyboard_index].remove(self.screen_image)

        old_index = self.keyboard_index
        self.remove(self.keyboards[self.keyboard_index])
        self.keyboard_index = index
        self.current_keyboard = self.keyboards[self.keyboard_index]
        self.add(self.current_keyboard)

        self.current_keyboard.update_layout()
        self.current_keyboard.update_image()
        self.current_keyboard.update_highlight(*self.keyboards[old_index].highlight.position)
        director.window.set_size(self.current_keyboard.window_width, self.current_keyboard.window_height)


"""The singleton; check ``keyboard.manager.KeyboardManager`` for details on usage.
Don't instantiate KeyboardManager(). Just use this singleton."""
manager = KeyboardManager()
