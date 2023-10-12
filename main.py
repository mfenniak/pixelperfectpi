#!/usr/bin/env python

from dependency_injector.wiring import Provide, inject
from di import Container
from pixelperfectpi import Clock
import socket

@inject
def main(clock: Clock = Provide[Container.clock]) -> None:
    clock.process()

# Main function
if __name__ == "__main__":
    with open("/proc/cpuinfo") as f:
        cpuinfo = f.read()
    if "Raspberry Pi" in cpuinfo:
        DEFAULT_EMULATED = "real"
    else:
        DEFAULT_EMULATED = "emulated"

    container = Container()

    container.config.mode.from_env("EMULATED", as_=str, default=DEFAULT_EMULATED)
    container.config.gpio.hardware_mapping.from_env("GPIO_HARDWARE_MAPPING", as_=str, default="regular")
    container.config.gpio.slowdown.from_env("GPIO_SLOWDOWN", as_=int, default=1)
    container.config.purpleair.url.from_env("PURPLEAIR_URL", as_=str, default="http://10.156.95.135/json")
    container.config.display_tz.from_env("DISPLAY_TZ", as_=str, default="America/Edmonton")
    container.config.calendar.ical_url.from_env("ICAL_URL", as_=str, required=True)
    container.config.font_path.from_env("FONT_PATH", as_=str, default="./fonts/")
    container.config.icon_path.from_env("ICON_PATH", as_=str, default="./icons/")
    container.config.mqtt.hostname.from_env("MQTT_HOST")
    container.config.mqtt.port.from_env("MQTT_PORT", as_=int, default=1883)
    container.config.mqtt.username.from_env("MQTT_USERNAME", as_=str)
    container.config.mqtt.password.from_env("MQTT_PASSWORD", as_=str)
    container.config.mqtt.discovery.prefix.from_env("MQTT_DISCOVERY_PREFIX", as_=str, default="homeassistant")
    container.config.mqtt.discovery.node_id.from_env("MQTT_DISCOVERY_NODE_ID", as_=str, default="pixelperfectpi")
    container.config.mqtt.discovery.object_id.from_env("MQTT_DISCOVERY_OBJECT_ID", as_=str, default=socket.gethostname())

    container.wire(modules=[__name__])
    main()
    container.shutdown_resources()
