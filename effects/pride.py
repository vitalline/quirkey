from typing import Optional

from PIL import Image, ImageChops
from PIL.ImageColor import getrgb

from effects.gradient import gradient_image

# Pride flag overlay! Works best as postprocessing and with white text.
# You can use HTML, RGB, HSL, HSV, or color names. See https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
gay = ['#E40303', '#FF8C00', '#FFED00', '#008026', '#004DFF', '#750787']
vincian = ['#078D70', '#26CEAA', '#98E8C1', '#F1EFFF', '#7BADE2', '#5049CC', '#3D1A78']
lesbian = ['#D52D00', '#EF7627', '#FF9A56', '#FFFFFF', '#D162A4', '#B55690', '#A30262']
trans = ['#5BCEFA', '#F5A9B8', '#FFFFFF', '#F5A9B8', '#5BCEFA']
nb = ['#FFF433', '#FFFFFF', '#9B59D0', '#2D2D2D']
fluid = ['#FF75A2', '#FFFFFF', '#BE18D6', '#000000', '#333EBD']
ace = ['#000000', '#959595', '#FFFFFF', '#660066']
aro = ['#3DA542', '#A8D379', '#FFFFFF', '#A9A9A9', '#000000']
agender = ['#000000', '#BCC4C6', '#FFFFFF', '#B6F583', '#FFFFFF', '#BCC4C6', '#000000']
# Feel free to add flags of your own choosing.

palette = gay  # choose your palette here!
multiplier = 5  # increase for sharper stripe edges
angle = 0  # in case you want your flag sideways?
colors = [getrgb(part) for part in palette for _ in range(multiplier)]  # don't touch unless you know what you're doing.


def process(image: Optional[Image.Image]) -> Optional[Image.Image]:
    if image is None:
        return
    overlay = gradient_image(image.width, image.height, colors, angle)
    overlay.putalpha(255)
    return ImageChops.multiply(image, overlay)
