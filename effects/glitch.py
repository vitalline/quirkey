from typing import Optional

from PIL import Image
from glitch_this import ImageGlitcher

glitch = ImageGlitcher()


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is not None:
        image = glitch.glitch_image(image, 2.5, color_offset=True)
    return image
