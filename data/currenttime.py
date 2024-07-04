from .resolver import DataResolver
from .weather import WeatherForecasts
from lxml import etree # type: ignore
from typing import Any
import aiohttp
import datetime
import time

class CurrentTimeDataResolver(DataResolver[float]):
    def __init__(self) -> None:
        self._frozen_time: float | None = None

    def freeze_time(self) -> None:
        self._frozen_time = time.time()

    def release_time(self) -> None:
        self._frozen_time = None

    @property
    def data(self):
        if self._frozen_time is not None:
            return self._frozen_time
        return time.time()
