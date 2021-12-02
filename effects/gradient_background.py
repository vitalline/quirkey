from PIL import Image

from effects.gradient import gradient_image

rainbow = [(255, 128, 128), (128, 255, 128), (128, 128, 255), (255, 128, 128)]


colors = [(0, 204, 102), (0, 102, 51)]
angle = 0


def process(image: Image.Image) -> Image.Image:
    background = gradient_image(image.width, image.height, colors, angle)
    background.putalpha(255)
    background.alpha_composite(image)
    return background
