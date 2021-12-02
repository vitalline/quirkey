from PIL import Image

color = (34, 34, 34)


def process(image: Image.Image) -> Image.Image:
    background = Image.new('RGB', (image.width, image.height), color)
    background.putalpha(255)
    background.alpha_composite(image)
    return background
