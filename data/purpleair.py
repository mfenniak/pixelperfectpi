from .resolver import ScheduledDataResolver
from typing import Any
import aiohttp
import re

RGB_RE = re.compile(r"rgb\((?P<red>[0-9]+),(?P<green>[0-9]+),(?P<blue>[0-9]+)\)")

class PurpleAirDataResolver(ScheduledDataResolver[dict[str, Any]]): # FIXME: change to a dataclass
    def __init__(self, url: str) -> None:
        assert url is not None
        super().__init__(refresh_interval=60)
        self.url = url

    async def do_collection(self) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                purpleair: dict[str, Any] = await response.json()

                color = purpleair["p25aqic"] # string, eg. rgb(87,237,0)
                m = RGB_RE.match(color)
                assert m is not None
                red, green, blue = int(m.group("red")), int(m.group("green")), int(m.group("blue")) 
                purpleair["p25aqic"] = (red, green, blue)

                purpleair["p25aqiavg"] = (purpleair['pm2.5_aqi'] + purpleair['pm2.5_aqi_b']) / 2

                temp_f = purpleair["current_temp_f"]
                # PurpleAir's API has a "Raw temperature".  https://community.purpleair.com/t/purpleair-sensors-functional-overview/150
                # They correct it -8 deg F to get a good approximation of ourdoor ambient temp.
                temp_f -= 8
                temp_c = (temp_f - 32) * 5 / 9
                purpleair["current_temp_c"] = temp_c

                # {'SensorId': '...',
                # 'p25aqic_b': 'rgb(55,234,0)'
                # 'pm2.5_aqi_b': 30
                # 'pm2.5_aqi': 35, 
                # 'p25aqic': 'rgb(87,237,0)', 
                # 'current_temp_f': 62, 
                return purpleair
