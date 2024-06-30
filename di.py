from component.aqi import AqiComponent
from component.calendar import CalendarComponent
from component.countdown import CountdownComponent
from component.currenttemp import CurrentTemperatureComponent
from component.dayofweek import DayOfWeekComponent
from component.distance import DistanceComponent
from component.door import DoorComponent
from component.media_player import MediaPlayerComponent
from component.oven import OvenOnComponent
from component.sunforecast import SunForecastComponent
from component.time import TimeComponent
from component.timer import TimerComponent
from component.weatherforecast import WeatherForecastComponent
from data.calendar import CalendarDataResolver
from data.distance import DistanceDataResolver
from data.door import DoorDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.media_player import MediaPlayerDataResolver
from data.ovenpower import OvenOnDataResolver
from data.purpleair import PurpleAirDataResolver
from data.timer import TimerDataResolver
from data.weather_mqtt import CurrentWeatherDataMqttResolver
from dependency_injector import containers, providers
from draw import MultiPanelPanel
from mqtt import MqttConfig, MqttServer
from pixelperfectpi import Clock
import asyncio
import datetime
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

    # purpleair = providers.Singleton(
    #     PurpleAirDataResolver,
    #     url=config.purpleair.url,
    # )

    current_weather = providers.Singleton(CurrentWeatherDataMqttResolver, topic=config.weather.mqtt_topic)

    display_tz = providers.Singleton(pytz.timezone, config.display_tz)

    calendar = providers.Singleton(
        CalendarDataResolver,
        ical_url=config.calendar.ical_url,
        display_tz=display_tz,
    )

    oven_on = providers.Singleton(OvenOnDataResolver)

    distance_to_mathieu = providers.Singleton(
        DistanceDataResolver,
        home_lat=config.location.latitude,
        home_long=config.location.longitude,
        topic="homeassistant/output/location/mathieu",
    )
    distance_to_amanda = providers.Singleton(
        DistanceDataResolver,
        home_lat=config.location.latitude,
        home_long=config.location.longitude,
        topic="homeassistant/output/location/amanda",
    )
    garage_door_status = providers.Singleton(
        DoorDataResolver,
        topic="homeassistant/output/door/garage_door",
    )
    garage_man_door_status = providers.Singleton(
        DoorDataResolver,
        topic="homeassistant/output/door/garage_man_door",
    )
    back_door_status = providers.Singleton(
        DoorDataResolver,
        topic="homeassistant/output/door/back_door",
    )
    media_player_status = providers.Singleton(
        MediaPlayerDataResolver,
        topic=config.homeassistant.media_mqtt_topic, # str | None
    )
    timer_status = providers.Singleton(
        TimerDataResolver,
        topic="homeassistant/output/timer/kitchen",
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
        data_resolver=current_weather,
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
    # aqi_component = providers.Singleton(
    #     AqiComponent,
    #     purpleair=purpleair,
    #     box=lower_position_inner,
    #     font_path=config.font_path,
    # )
    calendar_component = providers.Singleton(
        CalendarComponent,
        calendar=calendar,
        box=lower_position_inner,
        font_path=config.font_path,
        display_tz=display_tz,
    )
    # # weather_forecast_component = providers.Singleton(
    #     WeatherForecastComponent,
    #     env_canada=env_canada,
    #     box=lower_position_inner,
    #     font_path=config.font_path,
    # )
    # sun_forecast_component = providers.Singleton(
    #     SunForecastComponent,
    #     env_canada=env_canada,
    #     box=lower_position_inner,
    #     font_path=config.font_path,
    #     display_tz=display_tz,
    # )
    oven_component = providers.Singleton(
        OvenOnComponent,
        oven_on=oven_on,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    distance_to_mathieu_component = providers.Singleton(
        DistanceComponent,
        distance=distance_to_mathieu,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        label="Mathieu",
        icon="runner",
    )
    distance_to_amanda_component = providers.Singleton(
        DistanceComponent,
        distance=distance_to_amanda,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        label="Amanda",
        icon="cyclist",
    )
    garage_door_component = providers.Singleton(
        DoorComponent,
        door=garage_door_status,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Garage",
    )
    garage_man_door_component = providers.Singleton(
        DoorComponent,
        door=garage_man_door_status,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Man Door",
    )
    back_door_component = providers.Singleton(
        DoorComponent,
        door=back_door_status,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Back Door",
    )
    media_player_status_component = providers.Singleton(
        MediaPlayerComponent,
        media_player=media_player_status,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    timer_component = providers.Singleton(
        TimerComponent,
        timer=timer_status,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    paris_component = providers.Singleton(
        CountdownComponent,
        display_tz=display_tz,
        target_date=pytz.timezone("America/Edmonton").localize(datetime.datetime(2024, 6, 28, 19, 40, 0)),
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    lower_panels = providers.Singleton(
        MultiPanelPanel,
        panels=providers.List(
            # aqi_component,
            calendar_component,
            # weather_forecast_component,
            # sun_forecast_component,
            oven_component,
            distance_to_mathieu_component,
            distance_to_amanda_component,
            garage_door_component,
            garage_man_door_component,
            back_door_component,
            media_player_status_component,
            timer_component,
            paris_component,
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
        other_receivers=providers.List(
            oven_on,
            distance_to_mathieu,
            distance_to_amanda,
            garage_door_status,
            garage_man_door_status,
            back_door_status,
            media_player_status,
            timer_status,
            current_weather,
        ),
    )

    clock = providers.Singleton(
        Clock,
        data_resolvers=providers.List(
            # purpleair,
            # env_canada,
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
