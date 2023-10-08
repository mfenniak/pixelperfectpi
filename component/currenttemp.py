from data import PurpleAirDataResolver
from draw import DrawPanel, Box
from PIL import ImageColor
from typing import Any
import time

class CurrentTemperatureComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, purpleair: PurpleAirDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        assert purpleair is not None
        assert box is not None
        assert font_path is not None
        super().__init__(data_resolver=purpleair, box=box, font_path=font_path)
        self.load_font("7x13")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data is None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((0, 0, 0))
        if data is None:
            return
        curr_c = data["current_temp_c"]
        self.draw_text((128,128,128), f"{curr_c:.0f}°")
