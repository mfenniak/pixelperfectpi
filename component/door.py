from data import DoorDataResolver, DoorStatus
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from stretchable.style import AlignItems
import datetime
import pytz

class DoorComponent(ContainerNode, CarouselPanel):
    def __init__(self, door: DoorDataResolver, font_path: str, icon_path: str, name: str) -> None:
        super().__init__(
            flex_grow=1,
            align_items=AlignItems.STRETCH,
        )
        self.door = door
        self.name = name
        self.just_changed_timeframe = datetime.timedelta(seconds=10)
        self.left_open_timeframe = datetime.timedelta(minutes=5)
        self.add_child(self.DoorIcon(icon_path))
        self.add_child(self.DoorText(door, font_path, name, self.just_changed_timeframe, self.left_open_timeframe))

    def is_carousel_visible(self) -> bool:
        if self.door.data is None or self.door.data.status == DoorStatus.UNKNOWN:
            return False
        now_dt = datetime.datetime.now(pytz.utc)
        delta = now_dt - self.door.data.status_since
        if delta < self.just_changed_timeframe:
            return True
        if self.door.data.status == DoorStatus.OPEN and delta > self.left_open_timeframe:
            return True
        return False

    def priority(self) -> float:
        # For the first 15 seconds after the door status changes, we want to show the status.
        if self.door.data is None:
            return 0
        now_dt = datetime.datetime.now(pytz.utc)
        delta = now_dt - self.door.data.status_since
        if delta < self.just_changed_timeframe:
            return 10
        return 0

    class DoorIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="garage.png", background_color=(0, 32, 32))

    class DoorText(TextNode):
        def __init__(self, door: DoorDataResolver, font_path: str, name: str, just_changed_timeframe: datetime.timedelta, left_open_timeframe: datetime.timedelta) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.door = door
            self.name = name
            self.just_changed_timeframe = just_changed_timeframe
            self.left_open_timeframe = left_open_timeframe

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 32, 32)

        def get_text_color(self) -> tuple[int, int, int]:
            return (255, 128, 0)

        def get_text(self) -> str:
            if self.door.data is None:
                return ""
            now_dt = datetime.datetime.now(pytz.utc)
            delta = now_dt - self.door.data.status_since
            if delta < self.just_changed_timeframe:
                if self.door.data.status == DoorStatus.OPEN:
                    return f"{self.name} Opening"
                else:
                    return f"{self.name} Closed"
            else:
                return f"{self.name} Left Open"
