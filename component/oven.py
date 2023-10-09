from data import OvenOnDataResolver, OvenInformation, OvenStatus
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime

class OvenOnComponent(DrawPanel[OvenInformation]):
    def __init__(self, oven_on: OvenOnDataResolver, box: Box, font_path: str) -> None:
        super().__init__(data_resolver=oven_on, box=box, font_path=font_path)
        self.load_font("5x8")

    def frame_count(self, data: OvenInformation | None) -> int:
        if data is None:
            return 0
        if data.status != OvenStatus.ON:
            return 0
        return 1

    def do_draw(self, now: float, data: OvenInformation | None, frame: int) -> None:
        if data is None:
            return
        self.fill((32, 0, 0))
        self.draw_text((255, 0, 0), "Oven is on")
