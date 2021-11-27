from PIL import Image
from glitch_this import ImageGlitcher

glitch = ImageGlitcher()


def postprocess(image: Image.Image) -> Image.Image:
    image2 = glitch.glitch_image(image, 2.5, color_offset=True)
    return image2
