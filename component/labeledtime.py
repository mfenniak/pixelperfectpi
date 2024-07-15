from data import DataResolver
from draw import TextNode, CarouselPanel
from PIL import ImageColor
import time
import pytz
from datetime import datetime

class LabeledTimeComponent(TextNode, CarouselPanel):
    def __init__(self, font_path: str, current_time: DataResolver[float], display_tz: pytz.BaseTzInfo, label: str) -> None:
        assert font_path is not None
        assert current_time is not None
        super().__init__(
            font_path=font_path,
            font="6x10",
        )
        self.current_time = current_time
        self.display_tz = display_tz
        self.label = label

    def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        return (16, 0, 16)

    def get_text_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        return (0, 128, 0)

    def get_text(self) -> str:
        now = self.current_time.data
        assert now is not None
        dt = datetime.fromtimestamp(now, pytz.utc).astimezone(self.display_tz)
        timestr = dt.strftime("%-I:%M%p").lower()
        # if int(now % 2) == 0:
        #     timestr = timestr.replace(":", " ")
        return f"{self.label}: {timestr}"
