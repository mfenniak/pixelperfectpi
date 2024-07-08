from .drawpanel import Drawable
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints
from PIL import Image, ImageFont, ImageDraw
import os.path
from typing import TypeVar, Generic, Literal, Tuple

# horizontal or vertical enum
Orientation = Literal["horizontal", "vertical"]

class BarChart(Drawable):
    def __init__(self, orientation: Orientation, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.orientation = orientation

    def min_value(self) -> float:
        raise NotImplementedError
    
    def max_value(self) -> float:
        raise NotImplementedError
    
    def value(self) -> float | None:
        raise NotImplementedError

    def color_scale(self) -> list[tuple[float, tuple[int, int, int]]]:
        raise NotImplementedError

    def interpolate_color(self, value: float) -> tuple[int, int, int]:
        def lerp_color(start_color, end_color, t):
            return (
                int(start_color[0] + (end_color[0] - start_color[0]) * t),
                int(start_color[1] + (end_color[1] - start_color[1]) * t),
                int(start_color[2] + (end_color[2] - start_color[2]) * t)
            )
        color_scale = self.color_scale()
        prev = color_scale[0]
        for base_value, color in color_scale:
            if value <= base_value:
                if base_value == value:
                    return color
                return lerp_color(prev[1], color, (value - prev[0]) / (base_value - prev[0]))
            prev = base_value, color
        return prev[1]

    def do_draw(self) -> None:
        assert self.buffer is not None

        self.fill((0, 0, 0))

        my_min, my_max = self.min_value(), self.max_value()
        my_value = self.value()
        if my_value is None:
            return

        box = self.get_box(relative=True)
        width = int(box.width)
        height = int(box.height)

        if self.orientation == "horizontal":
            for x in range(0, width):
                value_x = (x / width) * (my_max - my_min)
                if value_x > my_value:
                    break
                color = self.interpolate_color(value_x)
                for y in range(0, height):
                    self.buffer.putpixel((x, y), color)
        elif self.orientation == "vertical":
            for y in range(0, height):
                value_y = (y / height) * (my_max - my_min)
                if value_y > my_value:
                    break
                color = self.interpolate_color(value_y)
                for x in range(0, width):
                    self.buffer.putpixel((x, height - y - 1), color)

