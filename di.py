from component.aqi import AqiComponent
from component.calendar import CalendarComponent
from component.currenttemp import CurrentTemperatureComponent
from component.dayofweek import DayOfWeekComponent
from component.sunforecast import SunForecastComponent
from component.time import TimeComponent
from component.weatherforecast import WeatherForecastComponent
from data.calendar import CalendarDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.purpleair import PurpleAirDataResolver
from dependency_injector import containers, providers
from draw import MultiPanelPanel
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

    lower_position_inner = (0, 0, 64, 19)
    lower_position = (0, 13, 64, 19)
    aqi_component = providers.Singleton(
        AqiComponent,
        purpleair=purpleair,
        box=lower_position_inner,
        font_path=config.font_path,
    )
    calendar_component = providers.Singleton(
        CalendarComponent,
        calendar=calendar,
        box=lower_position_inner,
        font_path=config.font_path,
        display_tz=display_tz,
    )
    weather_forecast_component = providers.Singleton(
        WeatherForecastComponent,
        env_canada=env_canada,
        box=lower_position_inner,
        font_path=config.font_path,
    )
    sun_forecast_component = providers.Singleton(
        SunForecastComponent,
        env_canada=env_canada,
        box=lower_position_inner,
        font_path=config.font_path,
        display_tz=display_tz,
    )
    lower_panels = providers.Singleton(
        MultiPanelPanel,
        panels=providers.List(
            aqi_component,
            calendar_component,
            weather_forecast_component,
            sun_forecast_component,
        ),
        box=lower_position,
        font_path=config.font_path,
    )

    clock = providers.Singleton(
        Clock,
        data_resolvers=providers.List(
            purpleair,
            env_canada,
            calendar,
        ),
        time_component=time_component,
        current_component=current_component,
        lower_panels=lower_panels,
    )
