from data import TimerDataResolver, TimerState, DataResolver
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from typing import Any
from PIL import ImageColor
import pytz
from datetime import datetime
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints

class CountdownComponent(ContainerNode, CarouselPanel):
    def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str, icon_path: str, **kwargs: Any) -> None:
        super().__init__()
        self.current_time = current_time
        self.target_date = target_date
        self.add_child(self.CountdownIcon(icon_path))
        self.add_child(self.CountdownText(current_time, target_date, font_path))

    def is_carousel_visible(self) -> bool:
        if self.current_time.data is None:
            return False
        now_dt = datetime.fromtimestamp(self.current_time.data, pytz.utc)
        if now_dt > self.target_date:
            return False
        else:
            return True

    class CountdownIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="france.png", background_color=(0, 32, 0))

    class CountdownText(TextNode):
        def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.current_time = current_time
            self.target_date = target_date

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 32, 0)

        def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
            now = self.current_time.data
            assert now is not None
            hue = int(now*50 % 360)
            return ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        def get_text(self) -> str:
            now = self.current_time.data
            assert now is not None

            now_dt = datetime.fromtimestamp(now, pytz.utc)
            delta = self.target_date - now_dt

            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds // 60) % 60
            seconds = delta.seconds % 60

            return  f"{days}d {hours}h {minutes}m {seconds}s"
