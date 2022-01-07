from io import BytesIO
from math import ceil, sqrt
from os.path import isfile
from typing import Callable, Union

from PIL import Image
from cocos.sprite import Sprite
from pyglet.image import load


class Key(Sprite):
    def __init__(self, name: Union[None, str, list[Union[str, list[str]]]] = None, folder: str = 'util',
                 size: Union[None, int, float, tuple[Union[int, float], Union[int, float]]] = None,
                 preprocess: Callable[[Image.Image], Image.Image] = lambda x: x, **kwargs) -> None:
        self.empty = False
        if name in (None, []):
            self.empty = True
            name = 'none'
            folder = 'util'
        self.name = name
        self.folder = folder
        if type(name) == list:
            if type(name[0]) == list:
                grid_height = len(name)
                grid_width = max(len(row) for row in name)
                new_name = [string for row in name for string in (row + [''] * (len(row) - grid_width))]
            else:
                grid_width = ceil(sqrt(len(name)))
                grid_height = ceil(len(name) / grid_width)
                new_name = name[:] + [''] * (len(name) - grid_width * grid_height)
            if size is None:
                size = 64
            if type(size) in (int, float):
                img_size = round(size * grid_width), round(size * grid_height)
                size = (size, size)
            else:
                img_size = round(size[0] * grid_width), round(size[1] * grid_height)
            self.base_image = Image.new(mode='RGBA', size=img_size, color=(0, 0, 0, 0))
            for i, name_part in enumerate(new_name):
                image_part = Image.open(self.get_path(name_part))
                image_part = image_part.resize((
                    round(min(image_part.width / image_part.height, 1) * size[0]),
                    round(min(image_part.height / image_part.width, 1) * size[1])
                ))
                x, y = i % grid_width, i // grid_width
                self.base_image.paste(image_part, (
                    round(image_part.width * x + (size[0] - image_part.width) * (x + 0.5)),
                    round(image_part.height * y + (size[1] - image_part.height) * (y + 0.5))
                ))
            self.rename(new_name)
        else:
            self.base_image = Image.open(self.get_path())
            if size is None:
                img_size = self.base_image.width, self.base_image.height
            elif type(size) in (int, float):
                if self.base_image.height > size:
                    self.base_image = self.base_image.resize((
                        round(size / self.base_image.height * self.base_image.width),
                        round(size)
                    ))
                img_size = (round(size),)
            else:
                img_size = (round(size[0]), round(size[1]))
        self.base_image = self.base_image.convert('RGBA')
        self.base_image.format = 'PNG'
        image_buffer = preprocess(self.base_image) if not self.empty else self.base_image
        data_buffer = BytesIO()
        image_buffer.save(data_buffer, format='png')
        data_buffer.seek(0)
        super().__init__(load('temp.png', file=data_buffer), **kwargs)
        self.resize(*img_size)

    def get_path(self, name: str = None, folder: str = None) -> str:
        if name is None:
            name = self.name
        if folder is None:
            folder = self.folder
        path_string = 'keyboards/assets/{}/{}.png'
        if not isfile(path_string.format(folder, name)):
            name = name.split(':', 1)[0]
        if not isfile(path_string.format(folder, name)):
            if folder == self.folder and name == self.name:
                self.empty = True
            folder, name = 'util', 'none'
        return path_string.format(folder, name)

    def is_empty(self) -> bool:
        return self.empty

    def rename(self, new_name) -> None:
        if type(new_name) == list:
            new_name = repr(new_name)
        self.name = new_name

    def resize(self, height: Union[int, float], width: Union[None, int, float] = None) -> None:
        if width is None:
            self.scale_x = 1
            self.scale_y = 1
            self.scale = height * self.scale / max(self.height, self.width)
        else:
            self.scale = 1
            self.scale_x = width * self.scale_x / self.width
            self.scale_y = height * self.scale_y / self.height
