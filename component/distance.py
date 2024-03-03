from data import DistanceDataResolver, LocationDistance
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime
import os.path
from PIL import Image

class DistanceComponent(DrawPanel[LocationDistance]):
    def __init__(self, distance: DistanceDataResolver, box: Box, font_path: str, icon_path: str, label: str, icon: str) -> None:
        super().__init__(data_resolver=distance, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, f"{icon}.png"))
        self.label = label

    def frame_count(self, data: LocationDistance | None, now: float) -> int:
        if data is None:
            return 0
        if data.distance < 0.25:
            return 0
        return 1

    def do_draw(self, now: float, data: LocationDistance | None, frame: int) -> None:
        if data is None:
            return
        self.fill((64, 64, 64))
        self.draw_icon(self.icon)
        self.draw_text((255, 255, 0), f"{self.label} - {data.distance:.1f}km", pad_left=self.icon.width)
