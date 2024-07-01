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
from config import AppConfig
from data import DataResolver
from data.calendar import CalendarDataResolver
from data.distance import DistanceDataResolver
from data.door import DoorDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from data.media_player import MediaPlayerDataResolver
from data.ovenpower import OvenOnDataResolver
from data.purpleair import PurpleAirDataResolver
from data.timer import TimerDataResolver
from data.weather_mqtt import CurrentWeatherDataMqttResolver
from draw import MultiPanelPanel
from mqtt import MqttConfig, MqttServer, MqttMessageReceiver
from pixelperfectpi import Clock
from typing import List
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

def create_clock(config: AppConfig) -> Clock:
    # System configuration objects
    display_tz = pytz.timezone(config.display_tz)

    # Create data resolvers
    data_resolvers: List[DataResolver] = []
    current_weather = CurrentWeatherDataMqttResolver(
        topic=config.weather_mqtt_topic,
    )
    data_resolvers.append(current_weather)
    calendar_data = CalendarDataResolver(
        ical_url=config.calendar_ical_url,
        display_tz=display_tz,
    )
    data_resolvers.append(calendar_data)
    oven_on_data = OvenOnDataResolver()
    data_resolvers.append(oven_on_data)
    distance_to_mathieu_data = DistanceDataResolver(
        home_lat=config.location.latitude,
        home_long=config.location.longitude,
        topic="homeassistant/output/location/mathieu",
    )
    data_resolvers.append(distance_to_mathieu_data)
    distance_to_amanda_data = DistanceDataResolver(
        home_lat=config.location.latitude,
        home_long=config.location.longitude,
        topic="homeassistant/output/location/amanda",
    )
    data_resolvers.append(distance_to_amanda_data)
    garage_door_status_data = DoorDataResolver(
        topic="homeassistant/output/door/garage_door",
    )
    data_resolvers.append(garage_door_status_data)
    garage_man_door_status_data = DoorDataResolver(
        topic="homeassistant/output/door/garage_man_door",
    )
    data_resolvers.append(garage_man_door_status_data) 
    back_door_status_data = DoorDataResolver(
        topic="homeassistant/output/door/back_door",
    )
    data_resolvers.append(back_door_status_data)
    media_player_data = MediaPlayerDataResolver(
        topic=config.homeassistant_media_mqtt_topic,
    )
    data_resolvers.append(media_player_data)
    timer_data = TimerDataResolver(
        topic="homeassistant/output/timer/kitchen",
    )
    data_resolvers.append(timer_data)

    # Create components
    time_component = TimeComponent(
        box=(29, 0, 35, 13),
        font_path=config.font_path,
    )
    current_position = (0, 0, 29, 13)
    current_temperature_component = CurrentTemperatureComponent(
        box=current_position,
        data_resolver=current_weather,
        font_path=config.font_path,
    )
    day_of_week_component = DayOfWeekComponent(
        box=current_position,
        font_path=config.font_path,
    )
    current_component = MultiPanelPanel(
        panels=[
            current_temperature_component,
            day_of_week_component,
        ],
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
    calendar_component = CalendarComponent(
        calendar=calendar_data,
        box=lower_position_inner,
        font_path=config.font_path,
        display_tz=display_tz,
    )
    # weather_forecast_component = providers.Singleton(
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
    oven_component = OvenOnComponent(
        oven_on=oven_on_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    distance_component_mathieu = DistanceComponent(
        distance=distance_to_mathieu_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        label="Mathieu",
        icon="runner",
    )
    distance_component_amanda = DistanceComponent(
        distance=distance_to_amanda_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        label="Amanda",
        icon="cyclist",
    )
    door_component_garage = DoorComponent(
        door=garage_door_status_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Garage",
    )
    door_component_man = DoorComponent(
        door=garage_man_door_status_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Man Door",
    )
    door_component_back = DoorComponent(
        door=back_door_status_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
        name="Back Door",
    )
    media_player_component = MediaPlayerComponent(
        media_player=media_player_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    timer_component = TimerComponent(
        timer=timer_data,
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )
    paris_component = CountdownComponent(
        display_tz=display_tz,
        target_date=pytz.timezone("America/Edmonton").localize(datetime.datetime(2024, 6, 28, 19, 40, 0)),
        box=lower_position_inner,
        font_path=config.font_path,
        icon_path=config.icon_path,
    )

    # Create panels
    lower_panels = MultiPanelPanel(
        panels=[
            # aqi_component,
            calendar_component,
            # weather_forecast_component,
            # sun_forecast_component,
            oven_component,
            distance_component_mathieu,
            distance_component_amanda,
            door_component_garage,
            door_component_man,
            door_component_back,
            media_player_component,
            timer_component,
            paris_component,
        ],
        box=lower_position,
        font_path=config.font_path,
    )

    # RGB Matrix initialization
    if config.mode == "real":
        rgbmatrixoptions = real_rgbmatrixoptions_factory(
            cols=64,
            rows=32,
            hardware_mapping=config.gpio_hardware_mapping,
            gpio_slowdown=config.gpio_slowdown,
        )
        rgbmatrix_provider = lambda: rgbmatrix.RGBMatrix(options=rgbmatrixoptions)
    else:
        rgbmatrixoptions = emulated_rgbmatrixoptions_factory(
            cols=64,
            rows=32,
        )
        rgbmatrix_provider = lambda: RGBMatrixEmulator.RGBMatrix(options=rgbmatrixoptions)

    # Configure MQTT and event handling
    mqtt_config = MqttConfig(
        hostname=config.mqtt.hostname,
        port=config.mqtt.port,
        username=config.mqtt.username,
        password=config.mqtt.password,
        discovery_prefix=config.mqtt.discovery_prefix,
        discovery_node_id=config.mqtt.discovery_node_id,
        discovery_object_id=config.mqtt.discovery_object_id,
    )
    shutdown_event = asyncio.Event()
    mqtt_server = MqttServer(
        config=mqtt_config,
        shutdown_event=shutdown_event,
        other_receivers=[data for data in data_resolvers if isinstance(data, MqttMessageReceiver)]
    )

    # Create the clock system
    clock = Clock(
        data_resolvers=data_resolvers,
        time_component=time_component,
        current_component=current_component,
        lower_panels=lower_panels,
        rgbmatrix_provider=rgbmatrix_provider,
        shutdown_event=shutdown_event,
        services=[mqtt_server],
    )

    return clock
