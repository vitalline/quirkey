from math import cos, sin, radians

from PIL import Image, ImageDraw


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def rot_x(self, degrees):
        rad = radians(degrees)
        return self.x * cos(rad) + self.y * sin(rad)


class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        min_x, max_x = (x1, x2) if x1 < x2 else (x2, x1)
        min_y, max_y = (y1, y2) if y1 < y2 else (y2, y1)
        self.min = Point(min_x, min_y)
        self.max = Point(max_x, max_y)

    def min_max_rot_x(self, degrees):
        first = True
        min_d, max_d = None, None
        for x in [self.min.x, self.max.x]:
            for y in [self.min.y, self.max.y]:
                p = Point(x, y)
                rot_d = p.rot_x(degrees)
                if first:
                    min_d = rot_d
                    max_d = rot_d
                else:
                    min_d = min(min_d, rot_d)
                    max_d = max(max_d, rot_d)
                first = False
        return min_d, max_d

    width = property(lambda self: self.max.x - self.min.x)
    height = property(lambda self: self.max.y - self.min.y)


def gradient_color(min_val, max_val, val, color_palette):
    """ Computes intermediate RGB color of a value in the range of min_val
        to max_val (inclusive) based on a color_palette representing the range.
    """
    max_index = len(color_palette)-1
    delta = max_val - min_val
    if delta == 0:
        delta = 1
    v = float(val - min_val) / delta * max_index
    i1, i2 = int(v), min(int(v) + 1, max_index)
    (r1, g1, b1), (r2, g2, b2) = color_palette[i1], color_palette[i2]
    f = v - i1
    return int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1))


def degrees_gradient(im, rect, color_func, color_palette, degrees):
    min_val, max_val = 1, len(color_palette)
    delta = max_val - min_val
    rad = radians(degrees)
    draw = ImageDraw.Draw(im)
    if sin(rad) == 0:
        width = float(rect.width)
        for x in range(rect.min.x, rect.max.x + 1):
            f = (x - rect.min.x) / width
            val = min_val + f * delta
            color = color_func(min_val, max_val, val, color_palette)
            draw.line([
                (x, rect.min.y if cos(rad) > 0 else rect.max.y),
                (x, rect.min.y if cos(rad) < 0 else rect.max.y),
            ], fill=color)
    elif cos(rad) == 0:
        height = float(rect.height)
        for y in range(rect.min.y, rect.max.y + 1):
            f = (y - rect.min.y) / height
            val = min_val + f * delta
            color = color_func(min_val, max_val, val, color_palette)
            draw.line([
                (rect.min.x if sin(rad) > 0 else rect.max.x, y),
                (rect.min.x if sin(rad) < 0 else rect.max.x, y),
            ], fill=color)
    else:
        min_d, max_d = rect.min_max_rot_x(degrees)
        range_d = max_d - min_d
        for x in range(rect.min.x, rect.max.x + 1):
            for y in range(rect.min.y, rect.max.y + 1):
                p = Point(x, y)
                f = (p.rot_x(degrees) - min_d) / range_d
                val = min_val + f * delta
                color = color_func(min_val, max_val, val, color_palette)
                draw.point((x, y), color)


def gradient_image(width, height, color_palette, degrees):
    region = Rect(0, 0, width - 1, height - 1)
    x, y = region.max.x + 1, region.max.y + 1
    image = Image.new('RGB', (x, y), (255, 255, 255))
    degrees_gradient(image, region, gradient_color, color_palette, -degrees)
    return image.crop((0, 0, width, height))
