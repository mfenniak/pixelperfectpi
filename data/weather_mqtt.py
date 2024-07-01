# Weather data resolver that is read from MQTT; eg. provided by Home Assistant.
# Example HA automation: see weather-ha.yml

from dataclasses import dataclass
from typing import Any, Dict
import json
import datetime
import pytz
from aiomqtt import Client, Message
from mqtt import MqttMessageReceiver
from .weather import CurrentWeatherData
from .resolver import DataResolver

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
        return CurrentWeatherData(
            condition=current.get('condition'),
            temperature=current.get('temperature'),
            humidity=current.get('humidity'),
            pressure=current.get('pressure'),
            wind_bearing=current.get('wind_bearing'),
            wind_speed=current.get('wind_speed'),
            uv=current.get('uv'),
        )

# class ForecastWeatherDataMqttResolver(DataResolver[WeatherForecast], MqttMessageReceiver):
#     def __init__(self, topic: str) -> None:
#         self.data = {}
#         self.topic = topic

#     async def subscribe_to_topics(self, client: Client) -> None:
#         await client.subscribe(self.topic)

#     async def handle_message(self, message: Message) -> bool:
#         if str(message.topic) != self.topic:
#             return False
#         if not isinstance(message.payload, bytes):
#             return False
#         data = json.loads(message.payload)
#         self.data = self.parse_weather_data(data)
#         return True

#     def parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         current = data['current']
#         forecasts = data['forecasts']['daily']

#         # Create dictionary with current weather data
#         current_weather = {
#             'condition': current['condition'],
#             'temperature': current['temperature'],
#             'humidity': current['humidity'],
#             'pressure': current['pressure'],
#             'wind_bearing': current['wind_bearing'],
#             'wind_speed': current['wind_speed']
#         }

#         # Create list of forecasts
#         daily_forecasts = []
#         for forecast in forecasts:
#             forecast_data = {
#                 'condition': forecast['condition'],
#                 'datetime': forecast['datetime'],
#                 'humidity': forecast['humidity'],
#                 'precipitation': forecast['precipitation'],
#                 'temperature': forecast['temperature'],
#                 'templow': forecast.get('templow', None)  # templow may not be present
#             }
#             daily_forecasts.append(forecast_data)

#         # Return structured data
#         return {
#             'current': current_weather,
#             'forecasts': daily_forecasts
#         }
