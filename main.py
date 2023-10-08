#!/usr/bin/env python

from dependency_injector.wiring import Provide, inject
from di import Container
from pixelperfectpi import Clock

@inject
def main(clock: Clock = Provide[Container.clock]) -> None:
    clock.process()

# Main function
if __name__ == "__main__":
    cpuinfo = open("/proc/cpuinfo").read()
    if "Raspberry Pi" in cpuinfo:
        DEFAULT_EMULATED = "real"
    else:
        DEFAULT_EMULATED = "emulated"

    from di import Container
    container = Container()

    container.config.mode.from_env("EMULATED", as_=str, default=DEFAULT_EMULATED)
    container.config.gpio.hardware_mapping.from_env("GPIO_HARDWARE_MAPPING", as_=str, default="regular")
    container.config.gpio.slowdown.from_env("GPIO_SLOWDOWN", as_=int, default=1)
    container.config.purpleair.url.from_env("PURPLEAIR_URL", as_=str, default="http://10.156.95.135/json")
    container.config.display_tz.from_env("DISPLAY_TZ", as_=str, default="America/Edmonton")
    container.config.calendar.ical_url.from_env("ICAL_URL", as_=str, required=True)
    container.config.font_path.from_env("FONT_PATH", as_=str, default="./fonts/")

    container.wire(modules=[__name__])

    main()
