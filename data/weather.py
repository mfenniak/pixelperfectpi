# Generic weather data classes.

from dataclasses import dataclass
from typing import List
import datetime

@dataclass
class CurrentWeatherData:
    condition: None | str
    temperature: None | float # Celsius
    humidity: None | int # 0 - 100, percentage
    pressure: None | float # hPa
    wind_bearing: None | int
    wind_speed: None | float # km/h
    uv: None | int # UV index

@dataclass
class WeatherForecast:
    condition: None | str
    datetime: None | datetime.datetime
    humidity: None | int # 0 - 100, percentage
    pressure: None | float # hPa
    wind_bearing: None | int
    wind_speed: None | float # km/h
    precipitation: None | float # mm
    temperature_high: None | float # Celsius
    temperature_low: None | float # Celsius

@dataclass
class WeatherForecasts:
    daily: List[WeatherForecast]
    hourly: List[WeatherForecast]

@dataclass
class SunForecast:
    sunrise: None | datetime.datetime
    sunset: None | datetime.datetime
