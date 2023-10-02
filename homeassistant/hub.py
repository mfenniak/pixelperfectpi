"""A demonstration 'hub' that connects several devices."""
from __future__ import annotations

# In a real implementation, this would be in an external library that's on PyPI.
# The PyPI package needs to be included in the `requirements` section of manifest.json
# See https://developers.home-assistant.io/docs/creating_integration_manifest
# for more information.
# This dummy hub always returns 3 rollers.
import asyncio
import random
import websockets
import json
import uuid

from homeassistant.core import HomeAssistant
from .const import LOGGER


class Hub:
    """Dummy hub for Hello World example."""

    manufacturer = "Demonstration Corp"

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Init dummy hub."""
        self._host = host
        self._hass = hass
        self._name = host
        self._id = host.lower()
        self.rollers = [
            Roller(f"{self._id}_1", f"{self._name} 1", self),
            Roller(f"{self._id}_2", f"{self._name} 2", self),
            Roller(f"{self._id}_3", f"{self._name} 3", self),
        ]
        self.online = True

        self.last_status = "ON"
        # map cmd id -> async-callback when cmd is complete
        self.waiting_cmds = {}

        # func(event)
        self.event_receivers = []

        self.send_queue = asyncio.Queue()

        self.shutdown = asyncio.Event()
        self.run_forever_task = asyncio.create_task(self.run_forever())

    async def close(self):
        self.shutdown.set()
        await self.run_forever_task

    @property
    def hub_id(self) -> str:
        """ID for dummy hub."""
        return self._id

    async def run_forever(self):
        while not self.shutdown.is_set():
            try:
                await self.run_loop()
            except:
                # if we exited run_loop then something went wrong with our websocket
                # connection; we should try to re-establish it but first we need
                # to back-off and delay
                LOGGER.debug("%s: run_loop exception", self._name, exc_info=True)
                await asyncio.sleep(15)

    async def run_loop(self):
        uri = f"ws://{self._host}:8080"
        async with websockets.connect(uri) as websocket:
            send_queue_get = asyncio.create_task(self.send_queue.get())
            websocket_recv = asyncio.create_task(websocket.recv())
            shutdown_wait = asyncio.create_task(self.shutdown.wait())

            while not self.shutdown.is_set():
                aws = [ send_queue_get, websocket_recv, shutdown_wait ]
                await asyncio.wait(aws, return_when=asyncio.FIRST_COMPLETED)

                if send_queue_get.done():
                    send_msg = send_queue_get.result()
                    await websocket.send(json.dumps(send_msg))
                    send_queue_get = asyncio.create_task(self.send_queue.get())
                
                if websocket_recv.done():
                    recv_msg = websocket_recv.result()
                    websocket_recv = asyncio.create_task(websocket.recv())

                    msg = json.loads(recv_msg)
                    cmd_id = msg.get("cmd_id")
                    if cmd_id is not None:
                        fut = self.waiting_cmds.get(cmd_id)
                        if fut is not None:
                            del self.waiting_cmds[cmd_id]
                            fut.set_result(msg)
                    elif msg.get("event", False):
                        await self.fire_event(msg)
                    else:
                        LOGGER.warning("%s: unexpected message recv %r", self._name, msg)
    
    async def fire_event(self, event):
        status = event.get("status")
        if status is not None:
            self.last_status = status
        for receiver in self.event_receivers:
            try:
                receiver(event)
            except:
                LOGGER.warning("%s: exception in event_receivers", self._name, exc_info=True)

    async def test_connection(self) -> bool:
        uri = f"ws://{self._host}:8080"
        async with websockets.connect(uri) as websocket:
            await websocket.recv()
        return True

    async def send_cmd(self, cmd):
        cmd_id = uuid.uuid4().hex
        fut = asyncio.Future()
        self.waiting_cmds[cmd_id] = fut
        await self.send_queue.put({ "cmd_id": cmd_id, "cmd": cmd })
        await fut

    async def turn_on(self):
        await self.send_cmd("ON")

    async def turn_off(self):
        await self.send_cmd("OFF")


class Roller:
    """Dummy roller (device for HA) for Hello World example."""

    def __init__(self, rollerid: str, name: str, hub: Hub) -> None:
        """Init dummy roller."""
        self._id = rollerid
        self.hub = hub
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        self._target_position = 100
        self._current_position = 100
        # Reports if the roller is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.
        self.moving = 0

        # Some static information about this device
        self.firmware_version = f"0.0.{random.randint(1, 9)}"
        self.model = "Test Device"

    @property
    def roller_id(self) -> str:
        """Return ID for roller."""
        return self._id

    @property
    def position(self):
        """Return position for roller."""
        return self._current_position

    async def set_position(self, position: int) -> None:
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        self._target_position = position

        if position == 0:
            self._loop.create_task(self.hub.turn_off())
        else:
            self._loop.create_task(self.hub.turn_on())

        # Update the moving status, and broadcast the update
        self.moving = position - 50
        await self.publish_updates()

        self._loop.create_task(self.delayed_update())

    async def delayed_update(self) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        await asyncio.sleep(random.randint(1, 10))
        self.moving = 0
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        self._current_position = self._target_position
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        """Roller is online."""
        # The dummy roller is offline about 10% of the time. Returns True if online,
        # False if offline.
        return random.random() > 0.1

    @property
    def battery_level(self) -> int:
        """Battery level as a percentage."""
        return random.randint(0, 100)

    @property
    def battery_voltage(self) -> float:
        """Return a random voltage roughly that of a 12v battery."""
        return round(random.random() * 3 + 10, 2)

    @property
    def illuminance(self) -> int:
        """Return a sample illuminance in lux."""
        return random.randint(0, 500)
