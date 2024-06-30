from data import DataResolver, SunForecast
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime

class SunForecastComponent(DrawPanel[SunForecast]):
    def __init__(self, env_canada: DataResolver[SunForecast], display_tz: pytz.BaseTzInfo, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=env_canada, box=box, font_path=font_path)
        self.display_tz = display_tz
        self.load_font("5x8")

    def frame_count(self, data: SunForecast | None, now: float) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: SunForecast | None, frame: int) -> None:
        if data is None or data.sunrise is None or data.sunset is None:
            return

        now_dt = datetime.datetime.now(self.display_tz)
        sunrise = data.sunrise
        sunset = data.sunset

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
