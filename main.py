#!/usr/bin/env python

from config import AppConfig, LocationConfig, MQTTConfig
from di import create_clock
from typing import Literal
import os
import socket

def load_config() -> AppConfig:
    with open("/proc/cpuinfo") as f:
        cpuinfo = f.read()
    mode: Literal['real', 'emulated'] = "real" if "Raspberry Pi" in cpuinfo else "emulated"

    return AppConfig(
        mode="emulated" if os.environ.get("EMULATED") is not None else mode,
        gpio_hardware_mapping=os.environ.get("GPIO_HARDWARE_MAPPING", "regular"),
        gpio_slowdown=int(os.environ.get("GPIO_SLOWDOWN", 1)),
        purpleair_url=os.environ.get("PURPLEAIR_URL", "http://10.156.95.135/json"),
        display_tz=os.environ.get("DISPLAY_TZ", "America/Edmonton"),
        calendar_ical_url=os.environ["ICAL_URL"],  # This is required; ensure it is set in your environment
        font_path=os.environ.get("FONT_PATH", "./fonts/"),
        icon_path=os.environ.get("ICON_PATH", "./icons/"),
        mqtt=MQTTConfig(
            hostname=os.environ["MQTT_HOST"],
            port=int(os.environ.get("MQTT_PORT", 1883)),
            username=os.environ["MQTT_USERNAME"],
            password=os.environ["MQTT_PASSWORD"],
            discovery_prefix=os.environ.get("MQTT_DISCOVERY_PREFIX", "homeassistant"),
            discovery_node_id=os.environ.get("MQTT_DISCOVERY_NODE_ID", "pixelperfectpi"),
            discovery_object_id=os.environ.get("MQTT_DISCOVERY_OBJECT_ID", socket.gethostname())
        ),
        homeassistant_media_mqtt_topic=os.environ.get("HA_MEDIA_MQTT_TOPIC"),
        location=LocationConfig(
            latitude=float(os.environ.get("LATITUDE", 51.036476342750326)),
            longitude=float(os.environ.get("LONGITUDE", -114.1045886332063))
        ),
        weather_mqtt_topic=os.environ.get("WEATHER_MQTT_TOPIC", "homeassistant/output/weather/Calgary")
    )

def main(config: AppConfig) -> None:
    clock = create_clock(config)
    clock.process()

# Main function
if __name__ == "__main__":
    config = load_config()
    main(config)
