from data import CalendarDataResolver, DataResolver
from draw import TextNode, CarouselPanel
from PIL import ImageColor
from typing import Any
import datetime
import pytz

class CalendarComponent(TextNode, CarouselPanel):
    def __init__(self, calendar: CalendarDataResolver, current_time: DataResolver[float], display_tz: pytz.BaseTzInfo, font_path: str, calendar_index: int, **kwargs: Any) -> None:
        super().__init__(font="4x6", font_path=font_path)
        self.calendar = calendar
        self.current_time = current_time
        self.display_tz = display_tz
        self.calendar_index = calendar_index

    def my_event(self) -> Any | None:
        calendar = self.calendar.data
        if calendar is None:
            return None
        future_events = calendar.get("future_events", [])
        if self.calendar_index >= len(future_events):
            return None
        return future_events[self.calendar_index]

    def is_carousel_visible(self) -> bool:
        return self.my_event() is not None

    def get_text(self) -> str:
        event = self.my_event()
        if event is None:
            return ""

        (dt, summary) = event

        preamble = ""
        now_dt = datetime.datetime.now(self.display_tz)

        if dt.time() == datetime.time(0,0,0):
            # full day event probably
            if dt.date() == now_dt.date():
                preamble = "tdy"
            elif dt.date() == (now_dt + datetime.timedelta(days=1)).date():
                preamble = dt.strftime("tmw")
            elif (dt - now_dt) < datetime.timedelta(days=7):
                preamble = dt.strftime("%a")
            else:
                preamble = dt.strftime("%a %-d")
        else:
            # timed event
            if dt.date() == now_dt.date():
                preamble = dt.strftime("%-I:%M%p").replace(":00", "")
            elif dt.date() == (now_dt + datetime.timedelta(days=1)).date():
                preamble = dt.strftime("tmw %-I%p")
            elif (dt - now_dt) < datetime.timedelta(days=7):
                preamble = dt.strftime("%a %-I%p")
            else:
                preamble = dt.strftime("%a %-d")

        if preamble.endswith("M"): # PM/AM -> P/A; no strftime option for that
            preamble = preamble[:-1]
        if preamble.endswith("P") or preamble.endswith("A"): # lowercase this
            preamble = preamble[:-1] + preamble[-1].lower()

        text = f"{preamble}: {summary}"
        return text

    def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        return (0, 0, 16)

    def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        now = self.current_time.data
        assert now is not None
        hue = int(now*50 % 360)
        return ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")
