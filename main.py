#!/usr/bin/env python

from dependency_injector.wiring import Provide, inject
from di import Container
from pixelperfectpi import Clock

@inject
def main(clock: Clock = Provide[Container.clock]) -> None:
    clock.process()

# Main function
if __name__ == "__main__":
    from di import Container
    container = Container()

    container.config.purpleair.url.from_env("PURPLEAIR_URL", as_=str, default="http://10.156.95.135/json")
    container.config.display_tz.from_env("DISPLAY_TZ", as_=str, default="America/Edmonton")
    container.config.calendar.ical_url.from_env("ICAL_URL", as_=str, required=True)

    container.wire(modules=[__name__])

    main()