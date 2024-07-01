from dataclasses import dataclass, field
from typing import Literal

@dataclass
class MQTTConfig:
    hostname: str
    port: int
    username: str
    password: str
    discovery_prefix: str
    discovery_node_id: str
    discovery_object_id: str

@dataclass
class LocationConfig:
    latitude: float
    longitude: float

@dataclass
class AppConfig:
    mode: Literal["real"] | Literal["emulated"]
    gpio_hardware_mapping: str
    gpio_slowdown: int
    purpleair_url: str
    display_tz: str
    calendar_ical_url: str
    font_path: str
    icon_path: str
    mqtt: MQTTConfig
    homeassistant_media_mqtt_topic: str | None
    location: LocationConfig
    weather_mqtt_topic: str
