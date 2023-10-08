from dependency_injector import containers, providers
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.calendar import CalendarDataResolver
from component.time import TimeComponent
from pixelperfectpi import Clock
from component.dayofweek import DayOfWeekComponent
from component.currenttemp import CurrentTemperatureComponent
from draw import MultiPanelPanel

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

    current_position = (0, 0, 29, 13)
    current_temperature_component = providers.Singleton(
        CurrentTemperatureComponent,
        box=current_position,
        purpleair=purpleair,
        font_path=config.font_path,
    )
    day_of_week_component = providers.Singleton(
        DayOfWeekComponent,
        box=current_position,
        font_path=config.font_path,
    )
    current_component = providers.Singleton(
        MultiPanelPanel,
        panels=providers.List(
            current_temperature_component,
            day_of_week_component,
        ),
        box=current_position,
        font_path=config.font_path,
    )

    clock = providers.Singleton(
        Clock,
        purpleair=purpleair,
        env_canada=env_canada,
        calendar=calendar,
        time_component=time_component,
        current_component=current_component,
    )
