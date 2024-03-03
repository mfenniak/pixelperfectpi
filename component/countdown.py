from data import StaticDataResolver
from datetime import datetime
from draw import DrawPanel, Box
from typing import Any
import pytz
import os.path
from PIL import Image, ImageColor


class CountdownComponent(DrawPanel[datetime]):
    def __init__(self, target_date: datetime, display_tz: pytz.BaseTzInfo, box: Box, font_path: str, icon_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(target_date), box=box, font_path=font_path)
        self.display_tz = display_tz
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "france.png"))

    def frame_count(self, data: datetime | None, now: float) -> int:
        now_dt = datetime.fromtimestamp(now, pytz.utc)
        if data is None or now_dt > data:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: datetime | None, frame: int) -> None:
        if data is None:
            return

        now_dt = datetime.fromtimestamp(now, pytz.utc)
        delta = data - now_dt

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60

        # blue: #001E96
        # white: #FFFFFF
        # red: #EE2436
        # blue = (0, 30, 150)
        # white = (255, 255, 255)
        # red = (238, 36, 54)
        # self.buffer.paste(blue,  box=(0 * (self.w // 3), 0, 1 * (self.w // 3), self.h))
        # self.buffer.paste(white, box=(1 * (self.w // 3), 0, 2 * (self.w // 3), self.h))
        # self.buffer.paste(red,   box=(2 * (self.w // 3), 0, 3 * (self.w // 3), self.h))

        hue = int(now*50 % 360)
        color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        self.fill((0, 32, 0))
        self.draw_icon(self.icon)
        self.draw_text(color, f"{days}d {hours}h {minutes}m {seconds}s", pad_left=self.icon.width)
