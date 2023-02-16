from typing import Optional

from PIL import Image

from keyboard import manager

board_height = 5
board_width = 5
screen_height = 4
asset_folder = 'letters'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'main'
preview_keys = {
    'default': '../util/cell'
}
layouts = {
    'main': [
        ['82', '48', '49', '50', '51'],
        ['71', '52', '53', '54', '55'],
        ['66', '56', '57', '97', '98'],
        ['/sym', '99', '100', '101', '102'],
        ['/en_words', '/lat', '/lat_extra', '/cyr', '/ru_words'],
    ],
}
fixed_layout = True


def postprocess(image: Optional[Image.Image]) -> Optional[Image.Image]:
    manager.keyboard.update_layout()
    return image
