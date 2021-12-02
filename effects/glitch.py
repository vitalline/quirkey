from PIL import Image
from glitch_this import ImageGlitcher

glitch = ImageGlitcher()


def process(image: Image.Image) -> Image.Image:
    image = glitch.glitch_image(image, 2.5, color_offset=True)
    return image
