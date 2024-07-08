from data import DataResolver, CurrentWeatherData
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from typing import Any
from PIL import ImageColor
import pytz
import datetime
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints

class CurrentUvIndexComponent(ContainerNode, CarouselPanel):
    def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str) -> None:
        super().__init__()
        self.data_resolver = data_resolver
        self.add_child(self.UvTextComponent(data_resolver, font_path))
        # self.add_child(self.UvGraphComponent(data_resolver, box))

    def is_carousel_visible(self) -> bool:
        if self.data_resolver.data is None:
            return False
        if self.data_resolver.data.uv is None:
            return False
        return True

    class UvTextComponent(TextNode):
        def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str) -> None:
            super().__init__(font="4x6", font_path=font_path)
            self.data_resolver = data_resolver

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 0, 0)

        def get_text_color(self) -> tuple[int, int, int]:
            return (192, 191, 159)

        def get_text(self) -> str:
            if self.data_resolver.data is None or self.data_resolver.data.uv is None:
                return ""
            return f"UV {self.data_resolver.data.uv}"

    # class UvGraphComponent(DrawPanel[CurrentWeatherData]):
    #     def __init__(self, data_resolver: DataResolver[CurrentWeatherData], box: Box) -> None:
    #         super().__init__(data_resolver=data_resolver, box=box, font_path=None)

    #     def frame_count(self, data: CurrentWeatherData | None, now: float) -> int:
    #         if data is None:
    #             return 0
    #         else:
    #             return 1

    #     def do_draw(self, now: float, data: CurrentWeatherData | None, frame: int) -> None:
    #         self.fill((0, 0, 0))
    #         if data is None or data.uv is None:
    #             return

    #         for i in range(0, data.uv):
    #             color = self.interpolate_color(i)
    #             row = self.h - i - 1
    #             if row < 0:
    #                 break
    #             for x in range(0, self.w):
    #                 self.set_pixel(x, row, color)

    #     def interpolate_color(self, uv_index: int) -> tuple[int, int, int]:
    #         def lerp_color(start_color, end_color, t):
    #             return (
    #                 int(start_color[0] + (end_color[0] - start_color[0]) * t),
    #                 int(start_color[1] + (end_color[1] - start_color[1]) * t),
    #                 int(start_color[2] + (end_color[2] - start_color[2]) * t)
    #             )

    #         uv_colors = [
    #             (0, (0, 255, 0)),   # Green
    #             (3, (255, 255, 0)), # Yellow
    #             (6, (255, 165, 0)), # Orange
    #             (8, (255, 0, 0)),   # Red
    #             (10, (255, 0, 255)) # Fuschia
    #         ]
    #         prev = uv_colors[0]
    #         for uv, color in uv_colors:
    #             if uv_index <= uv:
    #                 if uv == uv_index:
    #                     return color
    #                 return lerp_color(prev[1], color, (uv_index - prev[0]) / (uv - prev[0]))
    #             prev = uv, color
    #         return prev[1]
