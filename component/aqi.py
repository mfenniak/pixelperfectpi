from data import PurpleAirDataResolver
from draw import DrawPanel, Box
from typing import Any

class AqiComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, purpleair: PurpleAirDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=purpleair, box=box, font_path=font_path)
        self.load_font("7x13")

    def frame_count(self, data: dict[str, Any] | None, now: float) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((0, 16, 0))
        if data is None:
            return
        (red, green, blue) = data["p25aqic"]
        textColor = (red, green, blue)
        aqi = data['p25aqiavg']
        self.draw_text(textColor, f"AQI {aqi:.0f}")
