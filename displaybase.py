import asyncio
import sys
from typing import Literal, List
from rgbmatrix import RGBMatrix # type: ignore
from dependency_injector.providers import Provider
from service import Service


class DisplayBase(object):
    def __init__(self, rgbmatrix_provider: Provider[RGBMatrix], shutdown_event: asyncio.Event, services: List[Service]) -> None:
        self.rgbmatrix_provider = rgbmatrix_provider
        self.services = services

        self.state: Literal["ON"] | Literal["OFF"] = "ON"
        self.turn_on_event: asyncio.Event | None = None
        self.shutdown_event = asyncio.Event()
        self.matrix: RGBMatrix | None = None

    async def run(self) -> None:
        raise NotImplementedError

    async def turn_on(self) -> None:
        if self.state == "ON":
            return
        assert self.turn_on_event is not None
        self.state = "ON"
        self.turn_on_event.set()
        for service in self.services:
            await service.status_update(self.state)
        self.turn_on_event = None

    async def turn_off(self) -> None:
        if self.state == "OFF":
            return
        assert self.turn_on_event is None
        self.turn_on_event = asyncio.Event()
        self.state = "OFF"
        for service in self.services:
            await service.status_update(self.state)

    def process(self) -> None:
        self.matrix = None
        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            asyncio.run(self.async_run())
        except KeyboardInterrupt:
            if self.matrix is not None:
                del self.matrix
            self.shutdown_event.set()
            return

    def pre_run(self) -> None:
        raise NotImplementedError

    async def update_data(self) -> None:
        raise NotImplementedError

    async def create_canvas(self, matrix: RGBMatrix) -> None:
        raise NotImplementedError

    async def draw_frame(self, matrix: RGBMatrix) -> None:
        raise NotImplementedError

    async def async_run(self) -> None:
        for service in self.services:
            await service.start(self)
        self.pre_run()
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            await self.update_data()

            if self.state == "OFF":
                if self.matrix is not None:
                    self.matrix.Clear()
                    del self.matrix
                    self.matrix = None

                # Wake when we're turned on...
                assert self.turn_on_event is not None
                turn_on_event_task = asyncio.create_task(self.turn_on_event.wait())
                # Wake after a bit just to do an update_data call...
                sleep_task = asyncio.create_task(asyncio.sleep(120))
                # Wait until either wake condition; doesn't matter which.
                await asyncio.wait([ turn_on_event_task, sleep_task ], return_when=asyncio.FIRST_COMPLETED)

            elif self.state == "ON":
                if self.matrix is None:
                    self.matrix = self.rgbmatrix_provider()
                    await self.create_canvas(self.matrix)

                await self.draw_frame(self.matrix)
                await asyncio.sleep(0.1)
