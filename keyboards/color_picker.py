from PIL import Image

from keyboard import manager

board_height = 6
board_width = 12
screen_height = 3
asset_folder = 'util'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'main'
preview_keys = {
    'default': 'cell'
}
layouts = {
    'main': [
        [f'cell:h{i * 10}' for i in range(12)],
        [f'cell:h{i * 10}' for i in range(12, 24)],
        [f'cell:h{i * 10}' for i in range(24, 36)],
        [f'cell:s{round(i * 100 / 11)}' for i in range(12)],
        [f'cell:v{round(i * 100 / 11)}' for i in range(12)],
        ['', '', '', 'en_words', 'lat', 'lat_extra', 'sym', 'cyr', 'ru_words'],
    ],
}
fixed_layout = True


def postprocess(image: Image.Image) -> Image.Image:
    manager.keyboard.update_layout()
    return image
