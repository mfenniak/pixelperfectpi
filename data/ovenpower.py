from .resolver import DataResolver
from aiomqtt import Client, Message
from dataclasses import dataclass
from enum import Enum, auto
from mqtt import MqttMessageReceiver
import json

class OvenStatus(Enum):
    UNKNOWN = auto()
    OFF = auto()
    ON = auto()

@dataclass
class OvenInformation:
    status: OvenStatus
    # Might add last time of notice here to allow the component to stop displaying if it's out of date

# FIXME: I think it'd make sense to subscribe to the MQTT alert channel which sends a non-retained
# event, and then convert it into a separate channel that represents the retained oven state...
# OR change the mqtt-bridge to be retained... but not sure I want to change that behaviour.
# The goal would be that if the clock restarts when the oven is on, it should continue to display
# that state.

class OvenOnDataResolver(DataResolver[OvenInformation], MqttMessageReceiver):
    def __init__(self) -> None:
        self.data = OvenInformation(status=OvenStatus.UNKNOWN)
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
            self.data = OvenInformation(status=OvenStatus.ON)
        else:
            self.data = OvenInformation(status=OvenStatus.OFF)
        return True
