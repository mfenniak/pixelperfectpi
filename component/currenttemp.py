from data import DataResolver
from data.weather import CurrentWeatherData
from draw import TextNode, CarouselPanel
from PIL import ImageColor
from typing import Any
import time

class CurrentTemperatureComponent(TextNode, CarouselPanel):
    def __init__(self, font_path: str, data_resolver: DataResolver[CurrentWeatherData]) -> None:
        assert font_path is not None
        assert data_resolver is not None
        super().__init__(
            font_path=font_path,
            font="7x13",
        )
        self.data_resolver = data_resolver

    def is_carousel_visible(self) -> bool:
        return self.data_resolver.data is not None and self.data_resolver.data.temperature is not None

    def get_text(self) -> str:
        data = self.data_resolver.data
        if data is None:
            return ""
        curr_c = data.temperature
        if curr_c is None:
            return ""
        return f"{curr_c:.0f}°"

    def do_draw(self) -> None:
        self.fill((0, 0, 0))
        self.draw_text((128,128,128), self.get_text())
