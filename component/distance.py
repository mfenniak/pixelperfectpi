from data import TimerDataResolver, TimerState, DistanceDataResolver
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from typing import Any
from PIL import ImageColor
import pytz
import datetime
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints

class DistanceComponent(ContainerNode, CarouselPanel):
    def __init__(self, distance: DistanceDataResolver, font_path: str, icon_path: str, label: str, icon: str) -> None:
        super().__init__()
        self.distance = distance
        self.label = label
        self.add_child(self.DistanceIcon(icon_path, icon))
        self.add_child(self.DistanceText(distance, font_path, label))

    def is_carousel_visible(self) -> bool:
        if self.distance.data is None:
            return False
        if self.distance.data.distance < 0.25:
            return False
        return True

    class DistanceIcon(IconNode):
        def __init__(self, icon_path: str, icon: str) -> None:
            super().__init__(icon_path=icon_path, icon_file=f"{icon}.png", background_color=(64, 64, 64))

    class DistanceText(TextNode):
        def __init__(self, distance: DistanceDataResolver, font_path: str, label: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.distance = distance
            self.label = label

        def get_background_color(self) -> tuple[int, int, int]:
            return (64, 64, 64)

        def get_text_color(self) -> tuple[int, int, int]:
            return (255, 255, 0)

        def get_text(self) -> str:
            if self.distance.data is None:
                return ""
            return f"{self.label} - {self.distance.data.distance:.1f}km"
