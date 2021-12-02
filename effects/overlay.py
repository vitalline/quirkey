from PIL import Image, ImageChops

color = (0, 192, 96)


def process(image: Image.Image) -> Image.Image:
    overlay = Image.new('RGB', (image.width, image.height), color)
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
