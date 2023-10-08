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
from mqtt import MqttConfig, MqttServer
from pixelperfectpi import Clock
import asyncio
import pytz
import rgbmatrix # type: ignore
try:
    import RGBMatrixEmulator # type: ignore
except ImportError:
    # Not available on non x86-64 systems; optional in flake.nix
    pass

def emulated_rgbmatrixoptions_factory(cols: int, rows: int) -> "RGBMatrixEmulator.RGBMatrixOptions":
    opts = RGBMatrixEmulator.RGBMatrixOptions()
    opts.cols = cols
    opts.rows = rows
    return opts

def real_rgbmatrixoptions_factory(cols: int, rows: int, hardware_mapping: str, gpio_slowdown: int) -> rgbmatrix.RGBMatrixOptions:
    opts = rgbmatrix.RGBMatrixOptions()
    opts.cols = cols
    opts.rows = rows
    opts.hardware_mapping = hardware_mapping
    opts.gpio_slowdown = gpio_slowdown
    return opts

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

    emulated_rgbmatrixoptions: providers.Provider["RGBMatrixEmulator.RGBMatrixOptions"] = providers.Singleton(
        emulated_rgbmatrixoptions_factory,
        cols=64,
        rows=32,
    )

    real_rgbmatrixoptions: providers.Provider[rgbmatrix.RGBMatrixOptions] = providers.Singleton(
        real_rgbmatrixoptions_factory,
        cols=64,
        rows=32,
        hardware_mapping=config.gpio.hardware_mapping,
        gpio_slowdown=config.gpio.slowdown,
    )

    rgbmatrixoptions = providers.Selector(
        config.mode,
        emulated=emulated_rgbmatrixoptions,
        real=real_rgbmatrixoptions,
    )

    rgbmatrix = providers.Selector(
        config.mode,
        # Callable so that when RGBMatrixEmulator is not imported (on PI), it isn't accessed
        emulated=providers.Callable(lambda **kwargs: RGBMatrixEmulator.RGBMatrix(**kwargs), options=rgbmatrixoptions),
        real=providers.Factory(rgbmatrix.RGBMatrix, options=rgbmatrixoptions),
    )

    mqtt_config = providers.Singleton(
        MqttConfig,
        hostname=config.mqtt.hostname,
        port=config.mqtt.port,
        username=config.mqtt.username,
        password=config.mqtt.password,
        discovery_prefix=config.mqtt.discovery.prefix,
        discovery_node_id=config.mqtt.discovery.node_id,
        discovery_object_id=config.mqtt.discovery.object_id,
    )

    shutdown_event = providers.Singleton(asyncio.Event)

    mqtt_server = providers.Singleton(
        MqttServer,
        config=mqtt_config,
        shutdown_event=shutdown_event,
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
        rgbmatrix_provider=rgbmatrix.provider,
        shutdown_event=shutdown_event,
        services=providers.List(
            mqtt_server
        )
    )
