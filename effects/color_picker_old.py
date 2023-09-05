from typing import Optional

from PIL import Image, ImageChops, ImageColor, ImageOps

from keyboard import manager

overlay_color = ['0', '55', '100']
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
                current_part = 'hsv'.find(key_value[0])
                if current_part == -1:
                    return image
                overlay_color[current_part] = key_value[1:]
                return None
            else:
                current_part = 'hsv'.find(key_value[0])
                if current_part == -1:
                    return image
                if color[current_part] != key_value[1:]:
                    image = ImageOps.expand(image, round(image.width * (char_scale - 1)))
                else:
                    image = ImageOps.expand(image, round(image.width * (char_scale - 1) / 3))
                color[current_part] = key_value[1:]
    h, s, v = tuple(color)
    overlay = Image.new('RGB', (image.width, image.height), ImageColor.getrgb(f'hsv({h}, {s}%, {v}%)'))
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
