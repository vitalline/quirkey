from typing import Optional

from PIL import Image, ImageChops, ImageColor, ImageOps

from keyboard import manager

overlay_color = list('fff')
current_char = 0
char_scale = 1.5


def process(image: Image.Image) -> Optional[Image.Image]:
    keyboard = manager.keyboard
    if 'words' in keyboard.name or 'words' in keyboard.current_key.name:
        return image
    if keyboard.current_key.name in (keyboard.backspace_key, keyboard.enter_key):
        return image
    global overlay_color, current_char
    color = overlay_color.copy()
    if keyboard.name == 'color_picker_rgb':
        key_name = keyboard.current_key.name
        if key_name.isnumeric() and key_name.isascii():
            key_name = chr(int(key_name))
            if keyboard.current_key_is_pressed:
                if key_name in 'RGB':
                    current_char = 'RGB'.index(key_name)
                elif key_name in '0123456789abcdef':
                    overlay_color[current_char] = key_name
                return None
            else:
                if key_name in 'RGB':
                    color = [color[i] if 'RGB'.index(key_name) == i else '0' for i in range(len(color))]
                    if 'RGB'[current_char] != key_name:
                        image = ImageOps.pad(image, (image.width, round(image.height * char_scale)))
                elif key_name in '0123456789abcdef':
                    if color[current_char] != key_name:
                        image = ImageOps.pad(image, (image.width, round(image.height * char_scale)))
                    color[current_char] = key_name
    overlay = Image.new('RGB', (image.width, image.height), ImageColor.getrgb('#' + ''.join(color)))
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
