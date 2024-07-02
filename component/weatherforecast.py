from data import WeatherForecast, WeatherForecasts, DataResolver, StaticDataResolver
from dataclasses import dataclass
from draw import DrawPanel, Box
from typing import Any, Iterable
import datetime
import pytz
import itertools

@dataclass
class ForecastWithLabel:
    forecast: WeatherForecast
    label: str

class DailyWeatherForecastComponent(DrawPanel[WeatherForecasts]):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts], box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=weather_forecast_data, box=box, font_path=font_path)
        self.load_font("4x6")

    def get_today_forecast(self, data: WeatherForecasts) -> WeatherForecast | None:
        now = datetime.datetime.now(tz=pytz.utc)
        for day in data.daily:
            if day.datetime is None:
                continue
            if day.datetime.date() == now.date():
                return day
        return None

    def get_tomorrow_forecast(self, data: WeatherForecasts) -> WeatherForecast | None:
        now = datetime.datetime.now(tz=pytz.utc)
        for day in data.daily:
            if day.datetime is None:
                continue
            if day.datetime.date() == (now + datetime.timedelta(days=1)).date():
                return day
        return None

    def get_valid_forecasts(self, data: WeatherForecasts) -> Iterable[ForecastWithLabel]:
        forecast = self.get_today_forecast(data)
        if forecast is not None:
            yield ForecastWithLabel(forecast, "tdy")
        forecast = self.get_tomorrow_forecast(data)
        if forecast is not None:
            yield ForecastWithLabel(forecast, "tmw")

    def frame_count(self, data: WeatherForecasts | None, now: float) -> int:
        if data is None:
            return 0
        return len(list(self.get_valid_forecasts(data)))

    def do_draw(self, now: float, data: WeatherForecasts | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        forecasts = list(self.get_valid_forecasts(data))
        # print(repr(forecasts))
        if frame < len(forecasts):
            self.draw_forecast(forecasts[frame])

    def draw_forecast(self, fwl: ForecastWithLabel) -> None:
        cond = fwl.forecast.condition.capitalize() if fwl.forecast.condition is not None else "Unknown"
        txt = f"{fwl.label}: {cond} H:{fwl.forecast.temperature_high:.0f}° L:{fwl.forecast.temperature_low:.0f}°"
        if fwl.forecast.precipitation is not None and fwl.forecast.precipitation > 0:
            txt += f" {fwl.forecast.precipitation:.0f}mm"
        self.draw_text((200, 200, 200), txt)


class HourlyWeatherForecastComponent(DrawPanel[WeatherForecasts]):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts], display_tz: pytz.BaseTzInfo, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=weather_forecast_data, box=box, font_path=font_path)
        self.load_font("4x6")

        # create four subpanels, each with our height, but 1/4th the width
        self.subpanels = []
        for i in range(4):
            subbox = (box[0] + i * box[2] // 4, box[1], box[2] // 4, box[3])
            subpanel = HourlyWeatherForecastSingleHourPanel(data_resolver=weather_forecast_data, display_tz=display_tz, box=subbox, font_path=font_path)
            subpanel.load_font("4x6")
            self.subpanels.append(subpanel)

    def frame_count(self, data: WeatherForecasts | None, now: float) -> int:
        if data is None:
            return 0
        else:
            return 1

    def next_hours(self, data: WeatherForecasts) -> Iterable[WeatherForecast]:
        now = datetime.datetime.now(tz=pytz.utc)
        # round down now to the hour, so that the current hour's forecast is
        # included, unless the hour is nearly over... this doesn't always work
        # since sometimes HA will refresh and remove this hour's forecast since
        # it's current.
        if now.minute < 45:
            now = now.replace(minute=0, second=0, microsecond=0)
        for forecast in sorted(data.hourly, key=lambda f: f.datetime or datetime.datetime.min):
            if forecast.datetime is not None and now <= forecast.datetime:
                yield forecast

    def do_draw(self, now: float, data: WeatherForecasts | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        next_hours = [x for x in itertools.islice(self.next_hours(data), 4)]
        for i, forecast in enumerate(next_hours):
            self.subpanels[i].draw(self.buffer, now, forecast, 0)


class HourlyWeatherForecastSingleHourPanel(DrawPanel[WeatherForecast | None]):
    def __init__(self, box: Box, display_tz: pytz.BaseTzInfo, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        self.display_tz = display_tz
        self.load_font("4x6")

    def frame_count(self, data: WeatherForecast | None, now: float) -> int:
        if data is None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: WeatherForecast | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        self.draw_forecast(data)

    def draw_forecast(self, forecast: WeatherForecast) -> None:
        if forecast.datetime is None:
            return

        time_text = forecast.datetime.astimezone(self.display_tz).strftime("%-I%p")
        if time_text.endswith("M"): # PM/AM -> P/A; no strftime option for that
            time_text = time_text[:-1]
        if time_text.endswith("P") or time_text.endswith("A"): # lowercase this
            time_text = time_text[:-1] + time_text[-1].lower()
        self.draw_text(
            (200, 200, 200),
            time_text,
            valign="top",
        )

        if forecast.temperature_high is not None:
            self.draw_text(
                (200, 200, 200),
                f"{forecast.temperature_high:.0f}°",
                valign="middle",
            )

        if forecast.precipitation is not None and forecast.precipitation > 0:
            self.draw_text(
                (200, 200, 200),
                f"{forecast.precipitation:.0f}mm",
                valign="bottom",
            )
