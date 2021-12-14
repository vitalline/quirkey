from PIL import Image

from keyboard import manager

board_height = 5
board_width = 12
asset_folder = 'util'
backspace_key = 'backspace'
enter_key = 'enter'
default_layout = 'main'
preview_keys = {
    'default': 'cell'
}
layouts = {
    'main': [
        ['cell:h0', 'cell:h15', 'cell:h30', 'cell:h45', 'cell:h60', 'cell:h75',
         'cell:h90', 'cell:h105', 'cell:h120', 'cell:h135', 'cell:h150', 'cell:h165'],
        ['cell:h180', 'cell:h195', 'cell:h210', 'cell:h225', 'cell:h240', 'cell:h255',
         'cell:h270', 'cell:h285', 'cell:h300', 'cell:h315', 'cell:h330', 'cell:h345'],
        ['cell:s0', 'cell:s9', 'cell:s18', 'cell:s27', 'cell:s36', 'cell:s45',
         'cell:s55', 'cell:s64', 'cell:s73', 'cell:s82', 'cell:s91', 'cell:s100'],
        ['cell:v0', 'cell:v9', 'cell:v18', 'cell:v27', 'cell:v36', 'cell:v45',
         'cell:v55', 'cell:v64', 'cell:v73', 'cell:v82', 'cell:v91', 'cell:v100'],
        ['', '', '', 'en_words', 'lat', 'lat_extra', 'sym', 'cyr', 'ru_words'],
    ],
}


def postprocess(image: Image.Image) -> Image.Image:
    manager.keyboard.update_layout()
    return image
