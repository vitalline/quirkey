from typing import Optional

from PIL import Image, ImageChops

color = (0, 192, 96)


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is None:
        return
    overlay = Image.new('RGB', (image.width, image.height), color)
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
