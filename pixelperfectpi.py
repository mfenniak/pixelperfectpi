#!/usr/bin/env python

from samplebase import EMULATED, SampleBase

if EMULATED:
    from RGBMatrixEmulator import RGBMatrix, graphics # type: ignore
else:
    from rgbmatrix import RGBMatrix, graphics # type: ignore
from PIL import Image, ImageColor
import time
import asyncio
import datetime
import pytz
from typing import Set, TypeVar, Any
from data.resolver import StaticDataResolver
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.calendar import CalendarDataResolver

from draw import Box
from draw.drawpanel import DrawPanel
from draw.multipanelpanel import MultiPanelPanel


T = TypeVar('T')







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
