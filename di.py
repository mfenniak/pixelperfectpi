from dependency_injector import containers, providers
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.calendar import CalendarDataResolver
from pixelperfectpi import Clock

import pytz

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    purpleair = providers.Singleton(
        PurpleAirDataResolver,
        url=config.purpleair.url,
    )

    env_canada = providers.Singleton(EnvironmentCanadaDataResolver)

    display_tz = providers.Singleton(pytz.timezone, config.display_tz)

    calendar = providers.Singleton(
        CalendarDataResolver,
        ical_url=config.calendar.ical_url,
        display_tz=display_tz,
    )

    clock = providers.Singleton(
        Clock,
        purpleair=purpleair,
        env_canada=env_canada,
        calendar=calendar,
    )
