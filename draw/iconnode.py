from .drawpanel import Drawable
from PIL import Image
from stretchable.style.geometry.length import LengthPoints
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from typing import Literal
import os.path

class IconNode(Drawable):
    def __init__(self,
        icon_path: str,
        icon_file: str,
        background_color: tuple[int, int, int, int] | tuple[int, int, int] = (0, 0, 0),
        **kwargs) -> None:

        self.icon = Image.open(os.path.join(icon_path, icon_file))
        self.background_color = background_color

        super().__init__(
            measure=self.measure_node,
            **kwargs
        )

    def measure_node(self, size_points: SizePoints, size_available_space: SizeAvailableSpace) -> SizePoints:
        width, height = self.icon.width, self.icon.height
        # print(f"measure_node, size_points={size_points}, size_available_space={size_available_space}, returning {width=}, {height=}")
        return SizePoints(
            LengthPoints.points(width),
            LengthPoints.points(height)
        )

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
