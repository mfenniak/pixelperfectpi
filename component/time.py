from data import DataResolver
from draw import TextNode
from PIL import ImageColor
import time

class TimeComponent(TextNode):
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
        timestr = time.strftime("%-I:%M", time.localtime(now))
        if int(now % 2) == 0:
            timestr = timestr.replace(":", " ")
        return timestr

    def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        now = self.current_time.data
        assert now is not None
        hue = int(now*50 % 360)
        return ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

