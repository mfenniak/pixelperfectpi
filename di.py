from dependency_injector import containers, providers
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.calendar import CalendarDataResolver
from component.time import TimeComponent
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

    time_component = providers.Singleton(
        TimeComponent,
        box=(29, 0, 35, 13),
        # , **addt_config)
        font_path=config.font_path,
    )

    clock = providers.Singleton(
        Clock,
        purpleair=purpleair,
        env_canada=env_canada,
        calendar=calendar,
        time_component=time_component,
    )
