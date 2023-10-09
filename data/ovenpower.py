from dataclasses import dataclass
from .resolver import DataResolver
from enum import Enum, auto
import json
from mqtt import MqttMessageReceiver
from aiomqtt import Client, Message

class Status(Enum):
    UNKNOWN = auto()
    OFF = auto()
    ON = auto()

@dataclass
class OvenStatus:
    status: Status

class OvenOnDataResolver(DataResolver[OvenStatus], MqttMessageReceiver):
    def __init__(self) -> None:
        self.data = OvenStatus(status=Status.UNKNOWN)
        self.topic = "prometheus/alerts/OvenPoweredOn"

    async def maybe_refresh(self, now: float) -> None:
        return

    async def subscribe_to_topics(self, client: Client) -> None:
        await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False
        payload = json.loads(message.payload)
        alert_status = payload.get("status")
        if alert_status == "firing":
            self.data = OvenStatus(status=Status.ON)
        else:
            self.data = OvenStatus(status=Status.OFF)
        print("Received over power status update", self.data)
        return True
