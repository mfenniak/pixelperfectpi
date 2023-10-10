from .resolver import DataResolver
from aiomqtt import Client, Message
from dataclasses import dataclass
from enum import Enum, auto
from mqtt import MqttMessageReceiver
from typing import Literal
import datetime
import json
import math
import pytz

class DoorStatus(Enum):
    UNKNOWN = auto()
    OPEN = auto()
    CLOSED = auto()

@dataclass
class DoorInformation:
    status: DoorStatus
    status_since: datetime.datetime

class DoorDataResolver(DataResolver[DoorInformation], MqttMessageReceiver):
    def __init__(self, topic: str) -> None:
        self.data = DoorInformation(
            status=DoorStatus.UNKNOWN,
            status_since=datetime.datetime.now(pytz.utc)
        )
        self.topic = topic

    async def maybe_refresh(self, now: float) -> None:
        return

    async def subscribe_to_topics(self, client: Client) -> None:
        await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False

        assert self.data is not None

        payload = json.loads(message.payload)
        timestamp = datetime.datetime.strptime(payload.get("timestamp"), '%Y-%m-%d %H:%M:%S.%f%z')
        state: Literal["closed"] | Literal["open"] = payload.get("state")

        match state:
            case "closed":
                door_status = DoorStatus.CLOSED
            case "open":
                door_status = DoorStatus.OPEN
            case _:
                door_status = DoorStatus.UNKNOWN
        
        self.data = DoorInformation(status=door_status, status_since=timestamp)

        return True

# datetime.datetime.strptime('1985-04-12 23:20:50.288-06:00', '%Y-%m-%d %H:%M:%S.%f%z')
# homeassistant/output/door/garage_door { "timestamp": "2023-10-10 13:52:55.702056-06:00", "state": "closed" }
# homeassistant/output/door/garage_man_door { "timestamp": "2023-10-10 13:53:07.571062-06:00", "state": "closed" }
# homeassistant/output/door/back_door { "timestamp": "2023-10-10 13:54:19.102155-06:00", "state": "closed" }
