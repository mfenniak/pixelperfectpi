from data import EnvironmentCanadaDataResolver
from draw import DrawPanel, Box
from typing import Any
from data import WeatherForecast, WeatherForecasts, DataResolver
import datetime
import pytz

class WeatherForecastComponent(DrawPanel[WeatherForecasts]):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts], box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=weather_forecast_data, box=box, font_path=font_path)
        self.load_font("4x6")

    def get_tomorrow_forecast(self, data: WeatherForecasts) -> WeatherForecast | None:
        now = datetime.datetime.now(tz=pytz.utc)
        for day in data.daily:
            if day.datetime is None:
                continue
            if day.datetime.date() == (now + datetime.timedelta(days=1)).date():
                return day
        return None

    def frame_count(self, data: WeatherForecasts | None, now: float) -> int:
        panels = 0
        if data is not None and self.get_tomorrow_forecast(data) is not None:
            panels += 1 # one panel for the next day
        # if data is not None and data.hourly is not None and len(data.hourly) != 0:
        #     panels += 1 # one panel where we'll do ... something with hourly data
        return panels
        # if data == None:
        #     return 0
        # else:
        #     return 1

    def do_draw(self, now: float, data: WeatherForecasts | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        if frame == 0:
            self.draw_daily_forecast(data)
        # if frame == 1:
        #     self.draw_hourly_forecast(data)

    def draw_daily_forecast(self, data: WeatherForecasts) -> None:
        tomorrow = self.get_tomorrow_forecast(data)
        if tomorrow is None:
            return
        cond = tomorrow.condition.capitalize() if tomorrow.condition is not None else "Unknown"
        self.draw_text((255, 255, 255), f"Tomorrow: {cond} High {tomorrow.temperature_high:.0f}°")
