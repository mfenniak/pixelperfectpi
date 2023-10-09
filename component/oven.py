from data import OvenOnDataResolver, OvenInformation, OvenStatus
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime
import os.path
from PIL import Image

class OvenOnComponent(DrawPanel[OvenInformation]):
    def __init__(self, oven_on: OvenOnDataResolver, box: Box, font_path: str, icon_path: str) -> None:
        super().__init__(data_resolver=oven_on, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "oven-on.png"))

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
        # print("icon mode", self.icon.mode)
        self.draw_icon(self.icon)
        # self.buffer.alpha_composite(self.icon)
        self.draw_text((255, 0, 0), "Oven is on", pad_left=self.icon.width)
