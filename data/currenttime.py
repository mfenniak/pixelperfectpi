from .resolver import DataResolver
from lxml import etree # type: ignore
import time

class CurrentTimeDataResolver(DataResolver[float]):
    def __init__(self) -> None:
        self._frozen_time: float | None = None

    def freeze_time(self) -> None:
        self._frozen_time = time.time()

    def release_time(self) -> None:
        self._frozen_time = None

    @property
    def data(self) -> float | None: # type: ignore
        if self._frozen_time is not None:
            return self._frozen_time
        return time.time()
