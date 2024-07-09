from .drawable import Drawable
from typing import Literal

# horizontal or vertical enum
Orientation = Literal["horizontal", "vertical"]

class BarChart(Drawable):
    def __init__(self, orientation: Orientation, border: int = 0, border_color: tuple[int, int, int] = (0, 0, 0), *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.orientation = orientation
        self.border = border
        self.border_color = border_color

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
        for i in range(0, self.border):
            self.rect(self.border_color, i, i, self.buffer.width - i * 2, self.buffer.height - i * 2)

        my_min, my_max = self.min_value(), self.max_value()
        my_value = self.value()
        if my_value is None:
            return

        box = self.get_box(relative=True)
        width = int(box.width) - (self.border * 2)
        height = int(box.height) - (self.border * 2)

        if self.orientation == "horizontal":
            for x in range(0, width):
                value_x = (x / width) * (my_max - my_min)
                if value_x > my_value:
                    break
                color = self.interpolate_color(value_x)
                for y in range(0, height):
                    self.buffer.putpixel((self.border + x, self.border + y), color)
        elif self.orientation == "vertical":
            for y in range(0, height):
                # print(f"{y=}")
                value_y = (y / height) * (my_max - my_min)
                y_coord = height - y
                # print(f"{y=} {height=} {value_y=} {y_coord=} {my_value=}")
                if value_y > my_value:
                    break
                color = self.interpolate_color(value_y)
                for x in range(0, width):
                    # print(self.border + x, height - y - 1)
                    self.buffer.putpixel((self.border + x, height - y), color)
