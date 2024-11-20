# Weather data resolver that is read from MQTT; eg. provided by Home Assistant.
# Example HA automation: see weather-ha.yml

from .resolver import DataResolver
from .weather import CurrentWeatherData, WeatherForecasts, WeatherForecast
from aiomqtt import Client, Message
from mqtt import MqttMessageReceiver
from typing import Any, Dict
import datetime
import json

def translate_condition(cond: str | None) -> str | None:
    if cond is not None:
        if cond.lower() == "partlycloudy":
            return "Partly Cloudy"
    return cond

class CurrentWeatherDataMqttResolver(DataResolver[CurrentWeatherData], MqttMessageReceiver):
    def __init__(self, topic: str) -> None:
        self.data = CurrentWeatherData(
            condition=None,
            temperature=None,
            humidity=None,
            pressure=None,
            wind_bearing=None,
            wind_speed=None,
            uv=None,
        )
        self.topic = topic

    async def subscribe_to_topics(self, client: Client) -> None:
        # print("CurrentWeatherDataMqttResolver: Subscribing to topic", self.topic)
        await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        # print("CurrentWeatherDataMqttResolver: Received message: ", message.topic, message.payload)
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False
        data = json.loads(message.payload)
        self.data = self.parse_weather_data(data)
        # print("CurrentWeatherDataMqttResolver: Parsed data: ", self.data)
        return True

    def parse_weather_data(self, data: Dict[str, Any]) -> CurrentWeatherData:
        current = data['current']
        uv = current.get('uv')
        if isinstance(uv, str):
            try:
                uv = int(uv)
            except ValueError:
                uv = 0
        return CurrentWeatherData(
            condition=translate_condition(current.get('condition')),
            temperature=current.get('temperature'),
            humidity=current.get('humidity'),
            pressure=current.get('pressure'),
            wind_bearing=current.get('wind_bearing'),
            wind_speed=current.get('wind_speed'),
            uv=uv,
        )

class WeatherForecastDataMqttResolver(DataResolver[WeatherForecasts], MqttMessageReceiver):
    def __init__(self, topic: str) -> None:
        self.data = None
        self.topic = topic

    async def subscribe_to_topics(self, client: Client) -> None:
        # FIXME: technically we subscribe to the same weather topic twice
        # between both resolvers... it's OK... it does cause the messages to be
        # received and parsed twice.  Could be fixed maybe by making the Mqtt
        # client an abstraction that tracks the subscriptions in a set?
        await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        # print("WeatherForecastDataMqttResolver: Received message: ", message.topic)
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False
        data = json.loads(message.payload)
        self.data = self.parse_weather_data(data)
        return True

    def parse_weather_data(self, data: Dict[str, Any]) -> WeatherForecasts:
        retval = WeatherForecasts(
            daily=[],
            hourly=[]
        )
        forecasts = data.get("forecasts", {})
        daily = forecasts.get('daily', [])
        for day in daily:
            retval.daily.append(self.parse_weather_forecast(day))
        hourly = forecasts.get('hourly', [])
        for hour in hourly:
            retval.hourly.append(self.parse_weather_forecast(hour))
        # print("Weather forecast data: ", retval)
        return retval

    def parse_weather_forecast(self, data: Dict[str, Any]) -> WeatherForecast:
        return WeatherForecast(
            condition=translate_condition(data.get('condition')),
            datetime=self.parse_datetime(data.get('datetime')),
            humidity=data.get('humidity'),
            pressure=data.get('pressure'),
            wind_bearing=data.get('wind_bearing'),
            wind_speed=data.get('wind_speed'),
            precipitation=data.get('precipitation'),
            temperature_high=data.get('temperature'),
            temperature_low=data.get('templow')
        )

    def parse_datetime(self, dt: str | None) -> datetime.datetime | None:
        if dt is None:
            return None
        return datetime.datetime.fromisoformat(dt)

        # # Create list of forecasts
        # daily_forecasts = []
        # for forecast in forecasts:
        #     forecast_data = {
        #         'condition': forecast['condition'],
        #         'datetime': forecast['datetime'],
        #         'humidity': forecast['humidity'],
        #         'precipitation': forecast['precipitation'],
        #         'temperature': forecast['temperature'],
        #         'templow': forecast.get('templow', None)  # templow may not be present
        #     }
        #     daily_forecasts.append(forecast_data)

        # # Return structured data
        # return {
        #     'current': current_weather,
        #     'forecasts': daily_forecasts
        # }
