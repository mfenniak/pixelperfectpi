"""
Client-side asyncio library for accessing the pixelperfectpi's remote control API.
"""

# This should be in an external library, I guess... but I haven't used it for
# anything other than the Home Assistant component, so, it's fine.

import asyncio
import websockets
import json
import uuid

from .const import LOGGER

class Clock(object):
    def __init__(self, host: str) -> None:
        self._host = host
        self._name = host
        self.last_status = "ON" # reasonable guess?
        self.waiting_cmds = {} # map cmd id -> Future to finish when cmd is complete
        self.event_receivers = [] # func(event) callback list
        self.send_queue = asyncio.Queue()
        self.shutdown = asyncio.Event()
        self.run_forever_task = asyncio.create_task(self.run_forever())

    async def close(self):
        self.shutdown.set()
        await self.run_forever_task

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
                    LOGGER.debug("%s: get from send_queue: %r; transmitting", self._name, send_msg)
                    await websocket.send(json.dumps(send_msg))
                    send_queue_get = asyncio.create_task(self.send_queue.get())
                
                if websocket_recv.done():
                    recv_msg = websocket_recv.result()
                    websocket_recv = asyncio.create_task(websocket.recv())

                    msg = json.loads(recv_msg)
                    LOGGER.debug("%s: recv from websocket: %r", self._name, msg)
                    cmd_id = msg.get("cmd_id")
                    if cmd_id is not None:
                        LOGGER.debug("%s: recv has cmd_id=%s", self._name, cmd_id)
                        fut = self.waiting_cmds.get(cmd_id)
                        LOGGER.debug("%s: recv found matching fut=%r", self._name, fut)
                        if fut is not None:
                            del self.waiting_cmds[cmd_id]
                            LOGGER.debug("%s: fut set_result(%r)", self._name, msg)
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
        LOGGER.debug("%s/%s: dropping cmd into send_queue...", self._name, cmd_id)
        await self.send_queue.put({ "cmd_id": cmd_id, "cmd": cmd })
        LOGGER.debug("%s/%s: waiting for fut...", self._name, cmd_id)
        await fut
        LOGGER.debug("%s/%s: got fut result; completed send_cmd", self._name, cmd_id)

    async def turn_on(self):
        LOGGER.debug("%s: start turn_on", self._name)
        await self.send_cmd("ON")
        LOGGER.debug("%s: finish turn_on", self._name)

    async def turn_off(self):
        LOGGER.debug("%s: start turn_off", self._name)
        await self.send_cmd("OFF")
        LOGGER.debug("%s: finish turn_off", self._name)
