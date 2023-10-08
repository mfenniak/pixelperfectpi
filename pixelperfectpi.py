#!/usr/bin/env python

from samplebase import EMULATED, SampleBase

if EMULATED:
    from RGBMatrixEmulator import RGBMatrix, graphics # type: ignore
else:
    from rgbmatrix import RGBMatrix, graphics # type: ignore
from lxml import etree # type: ignore
from PIL import Image, ImageFont, ImageDraw, ImageColor
import time
import asyncio
import aiohttp
import icalendar # type: ignore
import datetime
import pytz
import recurring_ical_events # type: ignore
import os.path
from typing import Set, TypeVar, Generic, Any, Literal, Tuple
from data.resolver import DataResolver, ScheduledDataResolver, StaticDataResolver
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.calendar import CalendarDataResolver


T = TypeVar('T')




# x, y, w, h
Box = Tuple[int, int, int, int]

class DrawPanel(Generic[T]):
    def __init__(self, box: Box, font_path: str, data_resolver: DataResolver[T]) -> None:
        self.box = box
        self.font_path = font_path
        self.buffer = Image.new("RGB", (self.w, self.h))
        self.imagedraw = ImageDraw.Draw(self.buffer)
        self.pil_font: None | ImageFont.ImageFont = None
        self.data_resolver = data_resolver

    x = property(lambda self: self.box[0])
    y = property(lambda self: self.box[1])
    w = property(lambda self: self.box[2])
    h = property(lambda self: self.box[3])

    def load_font(self, name: str) -> None:
        self.pil_font = ImageFont.load(os.path.join(self.font_path, f"{name}.pil"))

    def frame_count(self, data: T | None) -> int:
        return 1

    def do_draw(self, now: float, data: T | None, frame: int) -> None:
        raise NotImplemented

    def draw(self, parent_buffer: Image.Image, now: float, data: T | None, frame: int) -> None:
        self.do_draw(now, data, frame)
        parent_buffer.paste(self.buffer, box=(self.x, self.y))

    def fill(self, color: tuple[int, int, int]) -> None:
        self.buffer.paste(color, box=(0,0,self.w,self.h))

    # halign - left, center, right
    # valign - top, middle, bottom
    def draw_text(self,
        color: tuple[int, int, int] | tuple[int, int, int, int], # RGB / RGBA
        text: str,
        halign: Literal["center"] | Literal["left"] | Literal["right"]="center",
        valign: Literal["top"] | Literal["middle"] | Literal["bottom"]="middle"
        ) -> None:

        if self.pil_font is None:
            raise Exception("must call load_font first")

        # measure the total width of the text...
        (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), text, font=self.pil_font, spacing=0, align="left")
        if right <= self.w:
            # it will fit in a single-line; nice and easy peasy...
            text_height = bottom
            if valign == "top":
                text_y = 0
            elif valign == "bottom":
                text_y = self.h - bottom
            else: # middle
                text_y = (self.h - text_height) // 2
            text_width = right
            if halign == "left":
                text_x = 0
            elif halign == "right":
                text_x = self.w - text_width
            else: # center
                text_x = (self.w - text_width) // 2
            self.imagedraw.multiline_text((text_x, text_y), text, fill=color, font=self.pil_font, spacing=0, align=halign)
            return

        # alright... let's just go line-by-line then, shall we.  First find the most text that will fit into one line,
        # word-by-word.
        lines = []
        text_words = text.split(" ")
        line = ""
        height_total = 0
        widest_line = 0
        while True:
            if len(text_words) == 0:
                # Ran out of words.
                if line != "":
                    height_total += bottom
                    lines.append(line)
                    (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
                    widest_line = max(widest_line, right)
                break

            next_word = text_words[0]
            proposed_line = line
            if proposed_line != "":
                proposed_line += " "
            proposed_line += next_word
            
            # will "proposed_line" fit onto a line?
            (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), proposed_line, font=self.pil_font, spacing=0, align="left")
            if right > self.w:
                height_total += bottom
                # no, proposed_line is too big; we'll make do with the last `line`
                if line != "":
                    lines.append(line)
                    (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
                    widest_line = max(widest_line, right)
                    line = ""
                    # leave next_word in text_words and keep going
                else:
                    # next_word by itself won't fit on a line; well, we can't skip the middle of a sentence so we'll
                    # just consume it regardless as it's own line.  Ignore it for widest_line calc.
                    lines.append(next_word)
                    text_words = text_words[1:]
            else:
                # yes, it will fit on the line
                line = proposed_line
                text_words = text_words[1:]

        new_text = "\n".join(lines)

        text_height = height_total
        if valign == "top":
            text_y = 0
        elif valign == "bottom":
            text_y = max(0, self.h - bottom)
        else: # middle
            text_y = max(0, (self.h - text_height) // 2)
        text_width = widest_line
        if halign == "left":
            text_x = 0
        elif halign == "right":
            text_x = max(0, self.w - text_width)
        else: # center
            text_x = max(0, (self.w - text_width) // 2)

        self.imagedraw.multiline_text((text_x, text_y), new_text, fill=color, font=self.pil_font, spacing=0, align=halign)


class MultiPanelPanel(DrawPanel[None]):
    # FIXME: correct types for panel_constructors
    def __init__(self, panel_constructors: Any, box: Box, font_path: str, time_per_frame: int = 5, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        # inner_kwargs = kwargs.copy()
        # # same width & height, but don't inherit the x/y position
        # inner_kwargs['x'] = 0
        # inner_kwargs['y'] = 0
        self.panels = [
            constructor(box=(0, 0, self.w, self.h), font_path=font_path, **kwargs) for constructor in panel_constructors
        ]
        self.time_per_frame = time_per_frame

    def do_draw(self, now: float, data: None, frame: int) -> None:
        # First; get a snapshot of the data for each panel so that it doesn't change while we're calculating this.
        panel_datas = [x.data_resolver.data for x in self.panels]

        # Ask each panel how many frames they will have, considering their data.
        frame_count: list[int] = [x.frame_count(data=panel_datas[i]) for i, x in enumerate(self.panels)]

        # Based upon the total number of frames on all panels, and the time, calculate the active frame.
        total_frames = sum(frame_count)

        if total_frames == 0:
            self.fill((0, 0, 0))
            return

        active_frame = int(now / self.time_per_frame) % total_frames

        # Find the panel for that frame, and the index of that frame in that panel.
        running_total = 0
        target_panel_index = None
        target_frame_index = None
        for panel_index, _frame_count in enumerate(frame_count):
            maybe_frame_index = active_frame - running_total
            if maybe_frame_index < _frame_count:
                target_panel_index = panel_index
                target_frame_index = maybe_frame_index
                break
            running_total += _frame_count
        assert target_panel_index is not None

        self.panels[target_panel_index].draw(self.buffer, now=now, data=panel_datas[target_panel_index], frame=target_frame_index)


class TimeComponent(DrawPanel[None]):
    def __init__(self, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        self.load_font("7x13")

    def do_draw(self, now: float, data: None, frame: int) -> None:
        self.fill((0, 0, 0))

        hue = int(now*50 % 360)
        color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        timestr = time.strftime("%-I:%M")
        if int(now % 2) == 0:
            timestr = timestr.replace(":", " ")
        self.draw_text(color, timestr, halign="right")


class DayOfWeekComponent(DrawPanel[None]):
    def __init__(self, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        self.load_font("7x13")

    def do_draw(self, now: float, data: None, frame: int) -> None:
        self.fill((0, 0, 0))

        # FIXME: color is synced to the time, but, only by copy-and-paste
        hue = int(now*50 % 360)
        color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        timestr = time.strftime("%a")
        self.draw_text(color, timestr)


class CurrentTemperatureComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, purpleair: PurpleAirDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=purpleair, box=box, font_path=font_path)
        self.load_font("7x13")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data is None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((0, 0, 0))
        if data is None:
            return
        curr_c = data["current_temp_c"]
        self.draw_text((128,128,128), f"{curr_c:.0f}°")


class AqiComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, purpleair: PurpleAirDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=purpleair, box=box, font_path=font_path)
        self.load_font("7x13")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((0, 16, 0))
        if data is None:
            return
        (red, green, blue) = data["p25aqic"]
        textColor = (red, green, blue)
        aqi = data['p25aqiavg']
        self.draw_text(textColor, f"AQI {aqi:.0f}")


class WeatherForecastComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, env_canada: EnvironmentCanadaDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=env_canada, box=box, font_path=font_path)
        self.load_font("4x6")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        n = data['forecast']['name']
        s = data['forecast']['text_summary']
        t = data['forecast']['type'].capitalize()
        deg_c = data['forecast']['deg_c']
        self.draw_text((255, 255, 255), f"{n} {s} {t} {deg_c:.0f}°")


class SunForecastComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, env_canada: EnvironmentCanadaDataResolver, display_tz: pytz.BaseTzInfo, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=env_canada, box=box, font_path=font_path)
        self.display_tz = display_tz
        self.load_font("5x8")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        if data is None:
            return

        now_dt = datetime.datetime.now(self.display_tz)
        sunrise = data['sunrise']
        sunset = data['sunset']

        if sunrise > now_dt and sunrise < sunset:
            self.fill((16, 16, 0))
            sun = "Sunrise"
            color = (255,167,0)
            dt = sunrise.astimezone(self.display_tz).strftime("%-I:%M")
        else:
            self.fill((0, 0, 16))
            sun = "Sunset"
            color = (80,80,169)
            dt = sunset.astimezone(self.display_tz).strftime("%-I:%M")
        self.draw_text(color, f"{sun} at {dt}")


class CalendarComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, calendar: CalendarDataResolver, display_tz: pytz.BaseTzInfo, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=calendar, box=box, font_path=font_path)
        self.display_tz = display_tz
        self.load_font("4x6")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data is None:
            return 0
        return min(len(data["future_events"]), 3) # no more than this many events

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((0, 0, 16))

        if data is None:
            return

        # FIXME: color is synced to the time, but, only by copy-and-paste
        hue = int(now*50 % 360)
        textColor = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        (dt, summary) = data["future_events"][frame]

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
        self.draw_text(textColor, text.encode("ascii", errors="ignore").decode("ascii"))


# TODO List:
# - Add icons - like a lightning bolt for power, or, sun^ sunv for high and low?
# - Animations - don't know where, when, but let's use all the pixels sometimes
# - Add capability for panels to have subpanels, since drawing ops are full panel size
# - Add something with an icon/image -- maybe the weather forecast
# New data:
# - Power: Usage, Solar Generation
# - Home Assistant: Back door / Garage door / etc. Open
# - Google Location: Distance to Mathieu?
# - Home Assistant: Presence
# - Countdown - France Flag & # days to France
# - Errors from any of the other data collectors / displayers
# - anxi - Any errors on Prometheus?


class Clock(SampleBase):
    def __init__(self, purpleair: PurpleAirDataResolver, env_canada: EnvironmentCanadaDataResolver, calendar: CalendarDataResolver) -> None:
        super().__init__()
        self.purpleair = purpleair
        self.env_canada = env_canada
        self.calendar = calendar

    def pre_run(self) -> None:
        self.data_resolvers = [
            self.purpleair,
            self.env_canada,
            self.calendar,
        ]
        self.background_tasks: Set[asyncio.Task[Any]] = set()

        addt_config={
            "font_path": self.font_path,
            "display_tz": self.display_tz,
        }
        self.time_component = TimeComponent((29, 0, 35, 13), **addt_config)
        self.curr_component = MultiPanelPanel(
            panel_constructors=[
                lambda **kwargs: CurrentTemperatureComponent(purpleair=self.purpleair, **kwargs),
                lambda **kwargs: DayOfWeekComponent(**kwargs),
            ],
            time_per_frame=5,
            box=(0, 0, 29, 13),
            **addt_config,
        )
        self.lower_panels = MultiPanelPanel(
            panel_constructors=[
                lambda **kwargs: AqiComponent(purpleair=self.purpleair, **kwargs),
                lambda **kwargs: CalendarComponent(calendar=self.calendar, **kwargs),
                lambda **kwargs: WeatherForecastComponent(env_canada=self.env_canada, **kwargs),
                lambda **kwargs: SunForecastComponent(env_canada=self.env_canada, **kwargs),
            ],
            time_per_frame=5,
            box=(0, 13, 64, 19),
            **addt_config,
        )

    async def create_canvas(self, matrix: RGBMatrix) -> None:
        self.offscreen_canvas = matrix.CreateFrameCanvas()
        self.buffer = Image.new("RGB", (self.offscreen_canvas.width, self.offscreen_canvas.height))

    async def update_data(self) -> None:
        now = time.time()
        for data_resolver in self.data_resolvers:
            task = asyncio.create_task(data_resolver.maybe_refresh(now))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    async def draw_frame(self, matrix: RGBMatrix) -> None:
        now = time.time()
        self.time_component.draw(self.buffer, now=now, frame=0, data=None) # FIXME: find a way to remove frame/data params
        self.curr_component.draw(self.buffer, now=now, frame=0, data=None)
        self.lower_panels.draw(self.buffer, now=now, frame=0, data=None)
        self.offscreen_canvas.SetImage(self.buffer, 0, 0)

        self.offscreen_canvas = matrix.SwapOnVSync(self.offscreen_canvas)
