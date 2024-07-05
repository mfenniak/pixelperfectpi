from data import DataResolver
from data.weather import CurrentWeatherData
from draw import TextNode
from PIL import ImageColor
from typing import Any
import time

class CurrentTemperatureComponent(TextNode):
    def __init__(self, font_path: str, data_resolver: DataResolver[CurrentWeatherData]) -> None:
        assert font_path is not None
        assert data_resolver is not None
        super().__init__(
            font_path=font_path,
            font="7x13",
        )
        self.data_resolver = data_resolver
        # self.last_text = ""

    # FIXME: when multi panel component is readded; give this a panel count of 0 when data_resolver.data is None
    # def frame_count(self, data: CurrentWeatherData | None, now: float) -> int:
    #     if data is None:
    #         return 0
    #     else:
    #         return 1

    def get_text(self) -> str:
        data = self.data_resolver.data
        if data is None:
            return ""
        curr_c = data.temperature
        if curr_c is None:
            return ""
        return f"{curr_c:.0f}°"

    def do_draw(self) -> None:
        # text = self.get_text()
        # if text != self.last_text:
        #     # FIXME: this seems like a hacky way to reforce layout -- ideally the container would ask before drawing
        #     self.mark_dirty()
        #     print("Text changing from ", self.last_text, "to", text)
        #     self.last_text = text
        self.fill((0, 0, 0))
        self.draw_text((128,128,128), self.get_text())
