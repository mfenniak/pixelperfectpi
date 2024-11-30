from data import DataResolver, CurrentWeatherData
from draw import TextNode, CarouselPanel, ContainerNode, BarChart
from stretchable.style import JustifyContent, AlignItems
from typing import Any

class CurrentWindChillIndexComponent(ContainerNode, CarouselPanel):
    def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str, **kwargs: Any) -> None:
        super().__init__(
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            **kwargs
        )
        self.data_resolver = data_resolver
        self.add_child(self.WindChillTextComponent(data_resolver, font_path))
        self.add_child(self.WindChillGraphComponent(data_resolver, margin=2))

    def is_carousel_visible(self) -> bool:
        if self.data_resolver.data is None:
            return False
        if self.data_resolver.data.uv is None:
            return False
        return True

    class WindChillTextComponent(TextNode):
        def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str) -> None:
            super().__init__(
                font="4x6",
                font_path=font_path,
                flex_grow=0,
                # debug_border=(128, 0, 0),
            )
            self.data_resolver = data_resolver

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 0, 0)

        def get_text_color(self) -> tuple[int, int, int]:
            return (192, 191, 159)

        def get_text(self) -> str:
            if self.data_resolver.data is None or self.data_resolver.data.wind_chill is None:
                return ""
            return f"WC\n{self.data_resolver.data.wind_chill:.0f}"

    class WindChillGraphComponent(BarChart):
        def __init__(self, data_resolver: DataResolver[CurrentWeatherData], **kwargs: Any) -> None:
            super().__init__(
                orientation="vertical",
                size=(5, 12),
                border=1,
                border_color=(19, 19, 15),
                flex_grow=0,
                **kwargs
            )
            self.data_resolver = data_resolver

        def min_value(self) -> float:
            return 0

        def max_value(self) -> float:
            return 60

        def value(self) -> float | None:
            if self.data_resolver.data is None:
                return None
            wc = self.data_resolver.data.wind_chill
            if wc is None or wc > 0:
                return None
            return -1 * wc

        def color_scale(self) -> list[tuple[float, tuple[int, int, int]]]:
            return [
                (0, (173, 216, 230)), # Light blue
                (60, (0, 0, 255))     # Deep blue
            ]
