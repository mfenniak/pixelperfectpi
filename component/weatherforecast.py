from data import WeatherForecast, WeatherForecasts, DataResolver
from draw import TextNode, CarouselPanel, ContainerNode
from stretchable.style import AlignItems, FlexDirection, JustifyContent
from typing import Any
import datetime
import pytz

class DailyWeatherForecastComponent(TextNode, CarouselPanel):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts], offset: datetime.timedelta, label: str, font_path: str, **kwargs: Any) -> None:
        super().__init__(font="4x6", font_path=font_path, flex_grow=1, **kwargs)
        self.weather_forecast_data = weather_forecast_data
        self.offset = offset
        self.label = label

    def get_forecast(self, data: WeatherForecasts | None) -> WeatherForecast | None:
        if data is None:
            return None
        now = datetime.datetime.now(tz=pytz.utc)
        for day in data.daily:
            if day.datetime is None:
                continue
            if day.datetime.date() == (now + self.offset).date():
                return day
        return None

    def is_carousel_visible(self) -> bool:
        return self.get_forecast(self.weather_forecast_data.data) is not None

    def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
        return (16, 0, 0)

    def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        return (200, 200, 200)

    def get_text(self) -> str:
        forecast = self.get_forecast(self.weather_forecast_data.data)
        if forecast is None:
            return "N/A"
        cond = forecast.condition.capitalize() if forecast.condition is not None else "Unknown"
        txt = f"{self.label}: {cond} H:{forecast.temperature_high:.0f}° L:{forecast.temperature_low:.0f}°"
        if forecast.precipitation is not None and forecast.precipitation > 0:
            if forecast.precipitation < 1:
                txt += " <1mm"
            else:
                txt += f" {forecast.precipitation:.0f}mm"
        return txt


class HourlyWeatherForecastComponent(ContainerNode, CarouselPanel):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts],  display_tz: pytz.BaseTzInfo, font_path: str, num_hours: int = 4, **kwargs: Any) -> None:
        super().__init__(
            flex_grow=1,
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            **kwargs,
        )
        self.weather_forecast_data = weather_forecast_data
        for i in range(num_hours):
            self.add_child(HourlyWeatherForecastSingleHourPanel(weather_forecast_data=weather_forecast_data, display_tz=display_tz, font_path=font_path, offset_hour=i+1))
        self.background_color = (16, 0, 0)

    def is_carousel_visible(self) -> bool:
        return self.weather_forecast_data.data is not None


def interpolate_color(temp: float) -> tuple[int, int, int]:
    """
    Converts a temperature (in Celsius) to an RGB color tuple.
    -40°C and below are deep blue.
    0°C is light blue.
    10°C is light green.
    20°C is green (ideal comfortable temperature).
    30°C is yellow.
    40°C and above is red.
    Supports temperatures from -40°C to 40°C.
    """
    # Define the color thresholds
    thresholds = [
        (-40, (0, 0, 255)),    # Deep blue
        (0, (173, 216, 230)),  # Light blue
        (10, (144, 238, 144)), # Light green
        (20, (0, 255, 0)),     # Green
        (30, (255, 255, 0)),   # Yellow
        (40, (255, 0, 0))      # Red
    ]
    
    # Find the two thresholds that the current temp lies between
    for i in range(len(thresholds) - 1):
        if thresholds[i][0] <= temp <= thresholds[i+1][0]:
            lower_temp, lower_color = thresholds[i]
            upper_temp, upper_color = thresholds[i+1]
            break
    else:
        # If temp is out of the bounds, clamp it
        if temp < -40:
            return thresholds[0][1]
        else:
            return thresholds[-1][1]
    
    # Perform linear interpolation between the two color thresholds
    factor = (temp - lower_temp) / (upper_temp - lower_temp)
    r = int(lower_color[0] + (upper_color[0] - lower_color[0]) * factor)
    g = int(lower_color[1] + (upper_color[1] - lower_color[1]) * factor)
    b = int(lower_color[2] + (upper_color[2] - lower_color[2]) * factor)
    
    return (r, g, b)


class HourlyWeatherForecastSingleHourPanel(ContainerNode, CarouselPanel):
    def __init__(self, weather_forecast_data: DataResolver[WeatherForecasts], display_tz: pytz.BaseTzInfo, font_path: str, offset_hour: int, **kwargs: Any) -> None:
        super().__init__(
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.STRETCH,
            **kwargs,
        )

        self.font_path = font_path
        self.weather_forecast_data = weather_forecast_data
        self.display_tz = display_tz
        self.offset_hour = offset_hour
        self.background_color = (16, 0, 0)

        self.add_child(self.HourText(self))
        self.add_child(self.TemperatureText(self))
        self.add_child(self.PrecipitationText(self))

    # FIXME? Maybe this should be cached briefly since it's accessed repeatedly by the three subframes
    def get_forecast(self) -> WeatherForecast | None:
        forecast = self.weather_forecast_data.data
        if forecast is None:
            return None
        now = datetime.datetime.now(pytz.utc).astimezone(self.display_tz)
        target_time = now + self.offset_hour * datetime.timedelta(hours=1)
        # print(f"Offset {self.offset_hour} is looking for {target_time}...")
        for hour in forecast.hourly:
            if hour.datetime is None:
                continue
            hour_time = hour.datetime.astimezone(self.display_tz)
            # print(f"\tFound {hour_time}...") 
            if hour_time.date() == target_time.date() and hour_time.hour == target_time.hour:
                # print("\tThat works!")
                return hour
        return None

    class HourText(TextNode):
        def __init__(self, hwparent: "HourlyWeatherForecastSingleHourPanel") -> None:
            super().__init__(font="4x6", font_path=hwparent.font_path)
            self.hwparent = hwparent

        def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
            return self.hwparent.background_color

        def get_text(self) -> str:
            forecast = self.hwparent.get_forecast()
            if forecast is None:
                return "N/A"
            assert forecast.datetime is not None
            text = forecast.datetime.astimezone(self.hwparent.display_tz).strftime("%-I%p")
            if text.endswith("M"): # PM/AM -> P/A; no strftime option for that
                text = text[:-1]
            if text.endswith("P") or text.endswith("A"): # lowercase this
                text = text[:-1] + text[-1].lower()
            return text

    class TemperatureText(TextNode):
        def __init__(self, hwparent: "HourlyWeatherForecastSingleHourPanel") -> None:
            super().__init__(font="4x6", font_path=hwparent.font_path)
            self.hwparent = hwparent

        def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
            return self.hwparent.background_color

        def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
            forecast = self.hwparent.get_forecast()
            if forecast is None:
                return (200, 200, 200)
            if forecast.temperature_high is None:
                return (200, 200, 200)
            return interpolate_color(forecast.temperature_high)

        def get_text(self) -> str:
            forecast = self.hwparent.get_forecast()
            if forecast is None:
                return "N/A"
            if forecast.temperature_high is None:
                return "N/A"
            return f"{forecast.temperature_high:.0f}°"


    class PrecipitationText(TextNode):
        def __init__(self, hwparent: "HourlyWeatherForecastSingleHourPanel") -> None:
            super().__init__(font="4x6", font_path=hwparent.font_path)
            self.hwparent = hwparent
        
        def get_background_color(self) -> tuple[int, int, int, int] | tuple[int, int, int]:
            return self.hwparent.background_color

        def get_text(self) -> str:
            forecast = self.hwparent.get_forecast()
            if forecast is None:
                return "N/A"
            if forecast.precipitation is None or forecast.precipitation == 0:
                return ""
            if forecast.precipitation < 1:
                return "<1mm"
            return f"{forecast.precipitation:.0f}mm"
