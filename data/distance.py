from .resolver import DataResolver
from aiomqtt import Client, Message
from dataclasses import dataclass
from mqtt import MqttMessageReceiver
import json
import math

# Helper function to calculate distance between two geographic coordinates using Haversine formula
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371  # Radius of Earth in km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = (math.sin(d_lat/2) * math.sin(d_lat/2) +
         math.sin(d_lon/2) * math.sin(d_lon/2) * math.cos(lat1) * math.cos(lat2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c

    return distance

@dataclass
class LocationDistance:
    distance: float  # distance in km

class DistanceDataResolver(DataResolver[LocationDistance], MqttMessageReceiver):
    def __init__(self, home_lat: float, home_long: float, topic: str) -> None:
        self.home_lat = home_lat
        self.home_long = home_long
        self.data = LocationDistance(distance=0.0)
        self.topic = topic

    async def maybe_refresh(self, now: float) -> None:
        return

    async def subscribe_to_topics(self, client: Client) -> None:
        await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False

        assert self.data is not None

        payload = json.loads(message.payload)
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")

        if latitude is None or longitude is None:
            self.data.distance = 0.0
        else:
            # Calculate the distance between the received point and hardcoded point
            distance = haversine_distance(latitude, longitude, self.home_lat, self.home_long)
            self.data.distance = distance

        return True
