import asyncio
import traceback
import random
from typing import TypeVar, Generic

T = TypeVar('T')

class DataResolver(Generic[T]):
    def __init__(self) -> None:
        self.data: None | T = None

    async def maybe_refresh(self, now: float) -> None:
        return

class ScheduledDataResolver(DataResolver[T]):
    def __init__(self, refresh_interval: float) -> None:
        jitter_frac = 1 + (random.random() * 0.2) # always jitter longer so we don't drop below refresh_interval
        self.refresh_interval = (refresh_interval * jitter_frac)
        self.last_refresh: float = 0
        self.lock = asyncio.Lock()
        self.data: None | T = None

    async def maybe_refresh(self, now: float) -> None:
        delta = now - self.last_refresh
        if delta > self.refresh_interval:
            try:
                await asyncio.wait_for(self.lock.acquire(), timeout=0.0000001)
                try:
                    await self.refresh()
                    self.last_refresh = now
                finally:
                    self.lock.release()
            except TimeoutError:
                pass

    async def do_collection(self) -> None | T:
        raise NotImplemented

    async def refresh(self) -> None:
        try:
            cr = self.do_collection()
            self.data = await cr
        except:
            # FIXME: log error
            print("do_collection error occurred")
            traceback.print_exc()
            self.data = None


class StaticDataResolver(DataResolver[T]):
    def __init__(self, static_data: T):
        super().__init__()
        self.data = static_data
