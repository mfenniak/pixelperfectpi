from data import DataResolver
from draw import TextNode, CarouselPanel
from PIL import ImageColor
from typing import Any
import time

class DayOfWeekComponent(TextNode, CarouselPanel):
    def __init__(self, font_path: str, current_time: DataResolver[float]) -> None:
        assert font_path is not None
        assert current_time is not None
        super().__init__(
            font_path=font_path,
            font="7x13",
        )
        self.current_time = current_time

    def get_text(self) -> str:
        now = self.current_time.data
        assert now is not None
        timestr = time.strftime("%a", time.localtime(now))
        return timestr

    def do_draw(self) -> None:
        self.fill((0, 0, 0))

        now = self.current_time.data
        assert now is not None

        # FIXME: color is synced to the time, but, only by copy-and-paste
        hue = int(now*50 % 360)
        color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        self.draw_text(color, self.get_text())
