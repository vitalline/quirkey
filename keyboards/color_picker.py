from typing import Optional

from PIL import Image

from keyboard import manager

board_height = 8
board_width = 14
screen_height = 3
key_size_multiplier = 0.8
asset_folder = 'util'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'main'
preview_keys = {
    'default': 'cell'
}
layouts = {
    'main': [
        [f'cell:h{i * 5}' for i in range(0, 12)],
        [f'cell:h{i * 5}' for i in range(12, 24)],
        [f'cell:h{i * 5}' for i in range(24, 36)],
        [f'cell:h{i * 5}' for i in range(36, 48)],
        [f'cell:h{i * 5}' for i in range(48, 60)],
        [f'cell:h{i * 5}' for i in range(60, 72)],
        [f'cell:s0.0, v{round(i * 100 / 16, 2)}' for i in range(0, 9)] + ['/lat', '/lat_extra', '/en_words'],
        [f'cell:s0.0, v{round(i * 100 / 16, 2)}' for i in range(8, 17)] + ['/cyr', '/sym', '/ru_words'],
    ],
}
for i, line in enumerate(layouts['main']):
    line.append(f'cell:s{round((8 - i) * 100 / 8, 1)}')
    line.append(f'cell:v{round((8 - i) * 100 / 8, 1)}')
fixed_layout = True


def postprocess(image: Optional[Image.Image]) -> Optional[Image.Image]:
    manager.keyboard.update_layout()
    return image
