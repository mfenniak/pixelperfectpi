from data import DataResolver
from datetime import datetime
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from PIL import ImageColor
from typing import Any
import pytz
from stretchable.style import AlignItems
from enum import Enum, auto

class CountDirection(Enum):
    DOWN = auto()
    UP = auto()

class CountdownComponent(ContainerNode, CarouselPanel):
    def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str, icon_path: str, count_direction: CountDirection = CountDirection.DOWN, **kwargs: Any) -> None:
        super().__init__(
            flex_grow=1,
            align_items=AlignItems.STRETCH,
        )
        self.current_time = current_time
        self.target_date = target_date
        print(repr(self.target_date))
        self.count_direction = count_direction
        self.add_child(self.CountdownIcon(icon_path))
        self.add_child(self.CountdownText(current_time, target_date, font_path, count_direction))

    def is_carousel_visible(self) -> bool:
        if self.current_time.data is None:
            return False
        now_dt = datetime.fromtimestamp(self.current_time.data, pytz.utc)
        if self.count_direction == CountDirection.DOWN and now_dt > self.target_date:
            return False
        elif self.count_direction == CountDirection.UP and now_dt < self.target_date:
            return False
        else:
            return True

    class CountdownIcon(IconNode):
        def __init__(self, icon_path: str, **kwargs: Any) -> None:
            super().__init__(icon_path=icon_path, icon_file="france.png", background_color=(0, 32, 0), **kwargs)

    class CountdownText(TextNode):
        def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str, count_direction: CountDirection, **kwargs: Any) -> None:
            super().__init__(font="5x8", font_path=font_path, **kwargs)
            self.current_time = current_time
            self.target_date = target_date
            self.count_direction = count_direction

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

            if self.count_direction == CountDirection.DOWN:
                delta = self.target_date - now_dt
            else:
                delta = now_dt - self.target_date

            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds // 60) % 60
            seconds = delta.seconds % 60

            return  f"{days}d {hours}h {minutes}m {seconds}s"
