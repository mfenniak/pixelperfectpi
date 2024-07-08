from data import TimerDataResolver, TimerState
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from stretchable.style import AlignItems
import datetime
import pytz

class TimerComponent(ContainerNode, CarouselPanel):
    def __init__(self, timer: TimerDataResolver, font_path: str, icon_path: str) -> None:
        super().__init__(
            flex_grow=1,
            align_items=AlignItems.CENTER,
        )
        self.timer = timer
        self.add_child(self.TimerIcon(icon_path))
        self.add_child(self.TimerText(timer, font_path))

    def is_carousel_visible(self) -> bool:
        if self.timer.data is None:
            return False
        if self.timer.data.state not in (TimerState.RUNNING, TimerState.PAUSED):
            return False
        if self.timer.data.state == TimerState.RUNNING and self.timer.data.finishes_at is not None and self.timer.data.finishes_at < datetime.datetime.now(pytz.utc):
            return False
        return True

    class TimerIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="timer.png", background_color=(37, 37, 14))

    class TimerText(TextNode):
        def __init__(self, timer: TimerDataResolver, font_path: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.timer = timer

        def get_background_color(self) -> tuple[int, int, int]:
            return (37, 37, 14)

        def get_text_color(self) -> tuple[int, int, int]:
            return (245, 191, 0)
        
        def get_text(self) -> str:
            if self.timer.data is None:
                return ""
            if self.timer.data.state == TimerState.RUNNING:
                if self.timer.data.finishes_at is None:
                    return ""
                remaining = self.timer.data.finishes_at - datetime.datetime.now(pytz.utc)
                remaining_minutes = int(remaining.total_seconds() / 60)
                remaining_seconds = int(remaining.total_seconds() % 60)
                return f"Timer {remaining_minutes}:{remaining_seconds:02}"
            else:
                if self.timer.data.remaining is None:
                    return ""
                remaining = self.timer.data.remaining
                remaining_minutes = int(remaining.total_seconds() / 60)
                remaining_seconds = int(remaining.total_seconds() % 60)
                return f"Paused {remaining_minutes}:{remaining_seconds:02}"
