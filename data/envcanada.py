from .resolver import ScheduledDataResolver
from .weather import WeatherForecasts
from lxml import etree # type: ignore
import aiohttp

class EnvironmentCanadaDataResolver(ScheduledDataResolver[WeatherForecasts]): # FIXME: change to a dataclass
    def __init__(self) -> None:
        super().__init__(refresh_interval=3600)

    async def fetch_xml(self) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dd.weather.gc.ca/citypage_weather/xml/AB/s0000047_e.xml') as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                return await response.read()

    async def do_collection(self) -> WeatherForecasts:
        # FIXME: not reimplemented yet
        return WeatherForecasts(hourly=[], daily=[])
        # xml_content = await self.fetch_xml()
        # root = etree.fromstring(xml_content)
        # elements = root.xpath("/siteData/forecastGroup/forecast")
        # # FIXME: handle missing/malformed data; no [0] without a good error; just set data to None
        # first_forecast = elements[0]
        # forecast_name = first_forecast.xpath("period[@textForecastName]")[0].values()[0] # "Today", "Tonight"
        # temperatures = first_forecast.xpath("temperatures/temperature")
        # text_summary = first_forecast.xpath("abbreviatedForecast/textSummary/text()")[0]
        # first_temperature = temperatures[0]

        # sunrise = root.xpath("/siteData/riseSet/dateTime[@zone='UTC' and @name='sunrise']/timeStamp/text()")[0]
        # (sunrise_year, sunrise_month, sunrise_day, sunrise_hour, sunrise_minute) = (sunrise[:4], sunrise[4:6], sunrise[6:8], sunrise[8:10], sunrise[10:12])
        # sunrise = datetime.datetime(int(sunrise_year), int(sunrise_month), int(sunrise_day), int(sunrise_hour), int(sunrise_minute), tzinfo=pytz.utc)

        # sunset = root.xpath("/siteData/riseSet/dateTime[@zone='UTC' and @name='sunset']/timeStamp/text()")[0]
        # (sunset_year, sunset_month, sunset_day, sunset_hour, sunset_minute) = (sunset[:4], sunset[4:6], sunset[6:8], sunset[8:10], sunset[10:12])
        # sunset = datetime.datetime(int(sunset_year), int(sunset_month), int(sunset_day), int(sunset_hour), int(sunset_minute), tzinfo=pytz.utc)

        # # Future: precipitation, snowLevel, windChill, uv, wind?
        # data = {
        #     "forecast": {
        #         "name": forecast_name, # Today, Tonight
        #         "type": first_temperature.get("class"), # high/low
        #         "deg_c": float(first_temperature.text),
        #         "text_summary": text_summary
        #     },
        #     "sunrise": sunrise,
        #     "sunset": sunset,
        # }
        # return data
