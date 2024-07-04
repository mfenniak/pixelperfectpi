from data import DataResolver
from draw import TextNode
from PIL import ImageColor
from typing import Any
import time

class TimeComponent(TextNode): # DrawPanel[None]):
    def __init__(self,
        # box: Box,
        font_path: str,
        current_time: DataResolver[float],
        # **kwargs: Any
        ) -> None:
        # assert box is not None
        assert font_path is not None
        assert current_time is not None
        super().__init__(
            # data_resolver=StaticDataResolver(None),
            # box=box,
            font_path=font_path,
            font="7x13",
        )
        self.current_time = current_time
        # self.load_font("7x13")

    def get_text(self) -> str:
        now = self.current_time.data
        assert now is not None
        timestr = time.strftime("%-I:%M", time.localtime(now))
        if int(now % 2) == 0:
            timestr = timestr.replace(":", " ")
        return timestr

    def do_draw(self) -> None:
        # assert self.buffer is not None
        # self.buffer.paste((32, 32, 0), box=(0,0,self.buffer.width,self.buffer.height))
        self.fill((0, 0, 0))
        # print("drawing text...")

        now = self.current_time.data
        assert now is not None

        hue = int(now*50 % 360)
        color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        self.draw_text(color, self.get_text()) # , halign="left", valign="top")

    # def do_draw(self, now: float, data: None, frame: int) -> None:
    #     self.fill((0, 0, 0))

    #     hue = int(now*50 % 360)
    #     color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

    #     timestr = time.strftime("%-I:%M")
    #     if int(now % 2) == 0:
    #         timestr = timestr.replace(":", " ")
    #     self.draw_text(color, timestr, halign="right")
