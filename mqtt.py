import json
import traceback
import asyncio
from asyncio_mqtt import Client
from dataclasses import dataclass
import backoff
import socket
import os
import config
import logging

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


def get_discovery_topic(config: MqttConfig):
    return f"{config.discovery_prefix}/switch/{config.discovery_node_id}/{config.discovery_object_id}/config"

def get_state_topic(config: MqttConfig):
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/state"

def get_cmd_topic(config: MqttConfig):
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/cmd"

def get_availability_topic(config: MqttConfig):
    return f"{config.discovery_prefix}/{config.discovery_node_id}/{config.discovery_object_id}/available"

def get_discovery_payload(config: MqttConfig):
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


class MqttServer(object):
    def __init__(self, config, clock):
        self.config = config
        self.clock = clock
        self.client = None

    def start(self):
        if self.config.hostname is None:
            return
        asyncio.create_task(self.serve_forever())

    async def serve_forever(self):
        while True:
            try:
                await self.connect_and_listen_mqtt()
            except Exception as e:
                print("Exception starting up connect_and_listen_mqtt", e)

    @backoff.on_exception(backoff.expo, Exception)  # Catch all exceptions
    async def connect_and_listen_mqtt(self):
        client = Client(
            hostname=self.config.hostname,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password
        )
        async with client:
            self.client = client
            await self.status_update(self.clock.state)

            try:
                if self.config.discovery_prefix is not None:
                    await client.publish(
                        get_discovery_topic(self.config),
                        json.dumps(get_discovery_payload(self.config)),
                        qos=1, retain=True)

                await client.publish(
                    get_availability_topic(self.config),
                    "online",
                    qos=1, retain=True)

                async with client.messages() as messages:
                    # Subscribe to the topic where we'll receive commands for the switch
                    await client.subscribe(get_cmd_topic(self.config))
                    async for message in messages:
                        cmd = message.payload.decode().upper()
                        if cmd == "ON":
                            await self.clock.turn_on()
                        elif cmd == "OFF":
                            await self.clock.turn_off()
            finally:
                self.client = None
                await client.publish(
                    get_availability_topic(self.config),
                    "offline",
                    qos=1, retain=True)
    
    async def status_update(self, state):
        if self.client is None:
            return
        await self.client.publish(get_state_topic(self.config), state, qos=1, retain=True)


def config_arg_parser(parser):
    parser.add_argument("--mqtt-host",
        help="MQTT hostname",
        default=os.environ.get("MQTT_HOST", getattr(config, "MQTT_HOST", None)),
        type=str)
    parser.add_argument("--mqtt-port",
        help="MQTT port",
        default=os.environ.get("MQTT_PORT", getattr(config, "MQTT_PORT", 1883)),
        type=int)
    parser.add_argument("--mqtt-username",
        help="MQTT username",
        default=os.environ.get("MQTT_USERNAME", getattr(config, "MQTT_USERNAME", None)),
        type=str)
    parser.add_argument("--mqtt-password",
        help="MQTT password",
        default=os.environ.get("MQTT_PASSWORD", getattr(config, "MQTT_PASSWORD", None)),
        type=str)
    parser.add_argument(
        "--mqtt-discovery-prefix",
        help="MQTT discovery prefix",
        default=os.environ.get("MQTT_DISCOVERY_PREFIX", getattr(config, "MQTT_DISCOVERY_PREFIX", "homeassistant")),
        type=str)
    parser.add_argument(
        "--mqtt-discovery-node-id",
        help="MQTT discovery node id",
        default=os.environ.get("MQTT_DISCOVERY_NODE_ID", getattr(config, "MQTT_DISCOVERY_NODE_ID", "pixelperfectpi")),
        type=str)
    parser.add_argument(
        "--mqtt-discovery-object-id",
        help="MQTT discovery object id",
        default=os.environ.get("MQTT_DISCOVERY_OBJECT_ID", getattr(config, "MQTT_DISCOVERY_OBJECT_ID", socket.gethostname())),
        type=str)


def get_config(args):
    return MqttConfig(
        hostname=args.mqtt_host,
        port=args.mqtt_port,
        username=args.mqtt_username,
        password=args.mqtt_password,
        discovery_prefix=args.mqtt_discovery_prefix,
        discovery_node_id=args.mqtt_discovery_node_id,
        discovery_object_id=args.mqtt_discovery_object_id,
    )
