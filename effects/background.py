from typing import Optional

from PIL import Image

color = (34, 34, 34)


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is None:
        return
    background = Image.new('RGB', (image.width, image.height), color)
    background.putalpha(255)
    background.alpha_composite(image)
    return background
