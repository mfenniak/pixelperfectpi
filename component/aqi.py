from data import PurpleAirDataResolver
from draw import TextNode, CarouselPanel
from typing import Any

class AqiComponent(TextNode, CarouselPanel):
    def __init__(self, purpleair: PurpleAirDataResolver, font_path: str, **kwargs: Any) -> None:
        super().__init__(font="7x13", font_path=font_path)
        self.purpleair = purpleair

    def is_carousel_visible(self) -> bool:
        return self.purpleair.data is not None

    def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        return (0, 16, 0)

    def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        if self.purpleair.data is None:
            return (255, 255, 255)
        (red, green, blue) = self.purpleair.data["p25aqic"]
        return (red, green, blue)

    def get_text(self) -> str:
        if self.purpleair.data is None:
            return "N/A"
        aqi = self.purpleair.data['p25aqiavg']
        return f"AQI {aqi:.0f}"
