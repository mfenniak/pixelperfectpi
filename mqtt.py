from aiomqtt import Client, Message
from dataclasses import dataclass
from service import Service
from typing import Any, Literal, TYPE_CHECKING
import asyncio
import backoff
import json
import logging

if TYPE_CHECKING:
    from displaybase import DisplayBase

logging.getLogger('backoff').addHandler(logging.StreamHandler())

@dataclass
class MqttConfig:
    hostname: str | None # None - mqtt disabled
    port: int
    username: str | None
    password: str | None

    discovery_prefix: str | None  # None - discovery disabled
    discovery_node_id: str | None
    discovery_object_id: str | None

class MqttMessageReceiver:
    async def subscribe_to_topics(self, client: Client) -> None:
        pass
    async def handle_message(self, message: Message) -> bool:
        return False

def get_discovery_topic(config: MqttConfig) -> str:
    return f"{config.discovery_prefix}/switch/{config.discovery_node_id}/{config.discovery_object_id}/config"

def get_state_topic(config: MqttConfig) -> str:
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/state"

def get_cmd_topic(config: MqttConfig) -> str:
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/cmd"

def get_availability_topic(config: MqttConfig) -> str:
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/available"

def get_discovery_payload(config: MqttConfig) -> dict[str, Any]:
    return {
        "name": config.discovery_object_id,
        "unique_id": f"pixelperfectpi_{config.discovery_object_id}",
        "state_topic": get_state_topic(config),
        "command_topic": get_cmd_topic(config),
        "availability_topic": get_availability_topic(config),
        "device": {
            "identifiers": [config.discovery_object_id],
            "name": "pixelperfectpi"
        }
    }

def on_runtime_error(e: Exception) -> bool:
    # give up when we have a RuntimeError because that can include the asyncio event loop shutting down
    return isinstance(e, RuntimeError)

class MqttServer(Service):
    def __init__(self, config: MqttConfig, shutdown_event: asyncio.Event, other_receivers: list[MqttMessageReceiver]):
        self.config = config
        self.shutdown_event = shutdown_event
        self.status_update_queue: asyncio.Queue[str] = asyncio.Queue()
        self.other_receivers = other_receivers

    async def start(self, clock: "DisplayBase") -> None:
        if self.config.hostname is None:
            return
        asyncio.create_task(self.serve_forever(clock))

    async def serve_forever(self, clock: "DisplayBase") -> None:
        while not self.shutdown_event.is_set():
            try:
                await self.connect_and_listen_mqtt(clock)
            except Exception as e:
                print("Exception starting up connect_and_listen_mqtt", e)

    @backoff.on_exception(backoff.expo, Exception, giveup=on_runtime_error, raise_on_giveup=False, max_time=300)  # Catch all exceptions
    async def connect_and_listen_mqtt(self, clock: "DisplayBase") -> None:
        assert self.config.hostname is not None
        client = Client(
            hostname=self.config.hostname,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password
        )
        async with client:
            await self.status_update(clock.state)

            try:
                await self.publish_discovery(client)
                await self.publish_availability(client, "online")
                await self.process_messages_forever(client, clock)
            finally:
                try:
                    await self.publish_availability(client, "offline")
                except:
                    # Best effort -- ignore any errors
                    pass

    async def publish_discovery(self, client: Client) -> None:
        if self.config.discovery_prefix is None:
            return
        await client.publish(
            get_discovery_topic(self.config),
            json.dumps(get_discovery_payload(self.config)),
            qos=1, retain=True)

    async def publish_availability(self, client: Client, availability: Literal["online"] | Literal["offline"]) -> None:
        await client.publish(
            get_availability_topic(self.config),
            availability,
            qos=1, retain=True)

    async def process_messages_forever(self, client: Client, clock: "DisplayBase") -> None:
        async with client.messages() as messages:
            # Subscribe to the topic where we'll receive commands for the switch
            cmd_topic = get_cmd_topic(self.config)
            await client.subscribe(cmd_topic)
            for other_receiver in self.other_receivers:
                await other_receiver.subscribe_to_topics(client)

            # this is correct, but create_task types are wrong? https://github.com/python/typeshed/issues/10185
            messages_next = asyncio.create_task(anext(messages)) # type: ignore
            status_update = asyncio.create_task(self.status_update_queue.get())
            shutdown_wait = asyncio.create_task(self.shutdown_event.wait())

            while not self.shutdown_event.is_set():
                aws = [ messages_next, status_update, shutdown_wait ]
                await asyncio.wait(aws, return_when=asyncio.FIRST_COMPLETED)

                if messages_next.done():
                    message = messages_next.result()
                    if str(message.topic) == cmd_topic:
                        cmd = message.payload.decode().upper()
                        if cmd == "ON":
                            await clock.turn_on()
                        elif cmd == "OFF":
                            await clock.turn_off()
                    else:
                        message_handled = False
                        for other_receiver in self.other_receivers:
                            if await other_receiver.handle_message(message):
                                message_handled = True
                                # Do not break; allow multiple receivers to handle the same message
                        if not message_handled:
                            print("Unknown message", message.topic, message.payload)
                    # this is correct, but create_task types are wrong? https://github.com/python/typeshed/issues/10185
                    messages_next = asyncio.create_task(anext(messages)) # type: ignore

                if status_update.done():
                    status = status_update.result()
                    await client.publish(get_state_topic(self.config), status, qos=1, retain=True)
                    status_update = asyncio.create_task(self.status_update_queue.get())

    async def status_update(self, state: Literal["ON"] | Literal["OFF"]) -> None:
        await self.status_update_queue.put(state)

# Prometheus alerts...
# topic: prometheus/alerts/PowerTest
# FIRING:   {"name":"PowerTest","url":"...","status":"firing","startsAt":"2023-10-09T01:57:52.676Z","endsAt":"0001-01-01T00:00:00Z"}
# RESOLVED: {"name":"PowerTest","url":"...","status":"resolved","startsAt":"2023-10-09T01:57:52.676Z","endsAt":"2023-10-09T02:01:52.676Z"}
