from data import DataResolver, SunForecast
from draw import TextNode, CarouselPanel
from typing import Any, Literal
import datetime
import pytz

class SunForecastComponent(TextNode, CarouselPanel):
    def __init__(self, sun_forecast: DataResolver[SunForecast], display_tz: pytz.BaseTzInfo, font_path: str, **kwargs: Any) -> None:
        super().__init__(font="5x8", font_path=font_path, flex_grow=1, **kwargs)
        self.sun_forecast = sun_forecast
        self.display_tz = display_tz

    def is_carousel_visible(self) -> bool:
        return self.sun_forecast.data is not None

    def mode(self) -> Literal["sunrise"] | Literal["sunset"]:
        if self.sun_forecast.data is None or self.sun_forecast.data.sunrise is None or self.sun_forecast.data.sunset is None:
            return "sunrise"
        now_dt = datetime.datetime.now(self.display_tz)
        sunrise = self.sun_forecast.data.sunrise
        sunset = self.sun_forecast.data.sunset
        if sunrise > now_dt and sunrise < sunset:
            return "sunrise"
        else:
            return "sunset"

    def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        if self.mode() == "sunrise":
            return (16, 16, 0)
        else:
            return (0, 0, 16)

    def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        if self.mode() == "sunrise":
            return (255, 167, 0)
        else:
            return (80, 80, 169)

    def get_text(self) -> str:
        if self.sun_forecast.data is None or self.sun_forecast.data.sunrise is None or self.sun_forecast.data.sunset is None:
            return "N/A"
        now_dt = datetime.datetime.now(self.display_tz)
        sunrise = self.sun_forecast.data.sunrise
        sunset = self.sun_forecast.data.sunset
        if sunrise > now_dt and sunrise < sunset:
            return f"Sunrise at {sunrise.astimezone(self.display_tz).strftime('%-I:%M')}"
        else:
            return f"Sunset at {sunset.astimezone(self.display_tz).strftime('%-I:%M')}"
