from colorsys import hsv_to_rgb
from math import ceil
from typing import Optional

from PIL import Image, ImageChops, ImageOps

from keyboard import manager

overlay_color = ['0', '50.0', '100.0']
char_scale = 1.5


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    keyboard = manager.keyboard
    if 'words' in keyboard.name or 'words' in keyboard.current_key.name:
        return image
    if keyboard.current_key.name in (keyboard.backspace_key, keyboard.enter_key):
        return image
    global overlay_color
    color = overlay_color.copy()
    if keyboard.name == 'color_picker':
        key = keyboard.current_key.name.split(':')
        if len(key) == 2 and key[0] == 'cell':
            key_value = key[1]
            if keyboard.current_key_is_pressed:
                parts = key_value.split(',')
                changed = False
                for part in parts:
                    part = part.strip()
                    current_part = 'hsv'.find(part[0])
                    if current_part != -1:
                        overlay_color[current_part] = part[1:]
                        changed = True
                return None if changed else image
            else:
                parts = key_value.split(',')
                found = False
                changed = False
                for part in parts:
                    part = part.strip()
                    current_part = 'hsv'.find(part[0])
                    if current_part != -1:
                        changed = changed or color[current_part] != part[1:]
                        found = True
                    color[current_part] = part[1:]
                if not found:
                    return image
                if changed:
                    image = ImageOps.expand(image, round(image.width * (char_scale - 1)))
                else:
                    image = ImageOps.expand(image, round(image.width * (char_scale - 1) / 3))
    h, s, v = tuple(map(float, color))
    color = tuple(ceil(x * 255) for x in hsv_to_rgb(h / 360, s / 100, v / 100))
    overlay = Image.new('RGB', (image.width, image.height), color)  # type: ignore
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
