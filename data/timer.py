# Home Assistant automation to send timer state to MQTT:
#
# alias: "MQTT Publish: Kitchen Timer"
# description: ""
# trigger:
#   - platform: state
#     entity_id:
#       - timer.kitchen
# condition: []
# action:
#   - service: mqtt.publish
#     data:
#       qos: "1"
#       retain: false
#       topic: homeassistant/output/timer/kitchen
#       payload: >-
#         { "state": "{{ states.timer.kitchen.state }}", "duration": "{{
#         state_attr('timer.kitchen', 'duration') or '' }}", "finishes_at": "{{
#         state_attr('timer.kitchen', 'finishes_at') or '' }}",
#         "remaining": "{{ state_attr('timer.kitchen', 'remaining') or '' }}" }
# mode: single

# when running:
# state == active
# duration == 0:18:00
# finishes_at == 2023-01-01T00:00:00+00:00
# remaining == 0:18:00

# when paused:
# state == paused
# duration == 0:18:00
# remaining == 0:09:17

# when cancelled or finished:
# state == idle
# duration == 0:18:00

from .resolver import DataResolver
from aiomqtt import Client, Message
from dataclasses import dataclass
from enum import Enum, auto
from mqtt import MqttMessageReceiver
import datetime
import json

class TimerState(Enum):
    UNKNOWN = auto()
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()

@dataclass
class TimerInformation:
    state: TimerState
    finishes_at: datetime.datetime | None
    remaining: datetime.timedelta | None
    duration: datetime.timedelta | None

class TimerDataResolver(DataResolver[TimerInformation], MqttMessageReceiver):
    def __init__(self, topic: str | None) -> None:
        self.data = TimerInformation(state=TimerState.UNKNOWN, finishes_at=None, remaining=None, duration=None)
        self.topic = topic

    async def maybe_refresh(self, now: float) -> None:
        return

    async def subscribe_to_topics(self, client: Client) -> None:
        if self.topic is not None:
            await client.subscribe(self.topic)

    async def handle_message(self, message: Message) -> bool:
        if str(message.topic) != self.topic:
            return False
        if not isinstance(message.payload, bytes):
            return False

        payload = json.loads(message.payload)
        match payload.get("state"):
            case "active":
                timer_state = TimerState.RUNNING
            case "paused":
                timer_state = TimerState.PAUSED
            case "idle":
                timer_state = TimerState.IDLE
            case _:
                timer_state = TimerState.UNKNOWN

        finishes_at = payload.get("finishes_at")
        if finishes_at is not None and finishes_at != "":
            finishes_at_dt = datetime.datetime.strptime(finishes_at, '%Y-%m-%dT%H:%M:%S%z')
        else:
            finishes_at_dt = None

        duration = payload.get("duration")
        if duration is not None and duration != "":
            duration_time = datetime.datetime.strptime(duration, '%H:%M:%S')
            duration_timedelta = datetime.timedelta(hours=duration_time.hour, minutes=duration_time.minute, seconds=duration_time.second)
        else:
            duration_timedelta = None

        remaining = payload.get("remaining")
        if remaining is not None and remaining != "":
            remaining_time = datetime.datetime.strptime(remaining, '%H:%M:%S')
            remaining_timedelta = datetime.timedelta(hours=remaining_time.hour, minutes=remaining_time.minute, seconds=remaining_time.second)
        else:
            remaining_timedelta = None

        self.data = TimerInformation(
            state=timer_state,
            finishes_at=finishes_at_dt,
            remaining=remaining_timedelta,
            duration=duration_timedelta,
        )
        return True
