from typing import Optional

from PIL import Image, ImageChops

from effects.gradient import gradient_image

rainbow = [(255, 128, 128), (128, 255, 128), (128, 128, 255), (255, 128, 128)]


colors = rainbow
angle = 0


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is None:
        return
    overlay = gradient_image(image.width, image.height, colors, angle)
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
