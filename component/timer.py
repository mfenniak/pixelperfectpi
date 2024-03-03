from data import TimerDataResolver, TimerInformation, TimerState
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime
import os.path
from PIL import Image

class TimerComponent(DrawPanel[TimerInformation]):
    def __init__(self, timer: TimerDataResolver, box: Box, font_path: str, icon_path: str) -> None:
        super().__init__(data_resolver=timer, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "timer.png"))

    def frame_count(self, data: TimerInformation | None, now: float) -> int:
        if data is None:
            return 0
        if data.state not in (TimerState.RUNNING, TimerState.PAUSED):
            return 0
        if data.state == TimerState.RUNNING and data.finishes_at is not None and data.finishes_at < datetime.datetime.now(pytz.utc):
            return 0
        return 1

    def do_draw(self, now: float, data: TimerInformation | None, frame: int) -> None:
        if data is None:
            return
        self.fill((37, 37, 14))
        text_color = (245, 191, 0)
        self.draw_icon(self.icon)
        if data.state == TimerState.RUNNING:
            if data.finishes_at is None:
                return
            # Calculate the remaining time
            remaining = data.finishes_at - datetime.datetime.now(pytz.utc)
            remaining_minutes = int(remaining.total_seconds() / 60)
            remaining_seconds = int(remaining.total_seconds() % 60)
            self.draw_text(text_color, f"Timer {remaining_minutes}:{remaining_seconds:02}", pad_left=self.icon.width)
        else:
            if data.remaining is None:
                return
            remaining = data.remaining
            remaining_minutes = int(remaining.total_seconds() / 60)
            remaining_seconds = int(remaining.total_seconds() % 60)
            self.draw_text(text_color, f"Paused {remaining_minutes}:{remaining_seconds:02}", pad_left=self.icon.width)

