from .drawpanel import Drawable
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints
from PIL import Image, ImageFont, ImageDraw
import os.path
from typing import TypeVar, Generic, Literal, Tuple

class IconNode(Drawable):
    def __init__(self,
        icon_path: str,
        icon_file: str,
        background_color: tuple[int, int, int, int] | tuple[int, int, int] = (0, 0, 0),
        *args,
        **kwargs) -> None:

        self.icon = Image.open(os.path.join(icon_path, icon_file))
        self.background_color = background_color
        super().__init__(size=(self.icon.width, self.icon.height), *args, **kwargs)

    def do_draw(self) -> None:
        assert self.buffer is not None

        self.fill(self.background_color)

        halign: Literal["center"] | Literal["left"] | Literal["right"] = "left"
        valign: Literal["top"] | Literal["middle"] | Literal["bottom"] = "middle"
        box = self.get_box(relative=True)
        dest = (0, 0)
        if halign == "center":
            dest = ((int(box.width) - self.icon.width) // 2, dest[1])
        elif halign == "right":
            dest = (int(box.width) - self.icon.width, dest[1])
        if valign == "middle":
            dest = (dest[0], (int(box.height) - self.icon.height) // 2)
        elif valign == "bottom":
            dest = (dest[0], int(box.height) - self.icon.height)
        self.buffer.alpha_composite(self.icon, dest)
