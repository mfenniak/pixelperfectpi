# Home Assistant automation to send media player state to MQTT:
# 
# alias: "MQTT Publish: Family Room TV State"
# description: ""
# trigger:
#   - platform: state
#     entity_id:
#       - media_player.family_room_tv
# condition: []
# action:
#   - service: mqtt.publish
#     data:
#       qos: "1"
#       retain: true
#       topic: homeassistant/output/media/family_room_tv
#       payload: >-
#         { "state": "{{ states.media_player.family_room_tv.state }}", "position":
#         {{ state_attr("media_player.family_room_tv", "media_position") if
#         state_attr("media_player.family_room_tv", "media_position") is not none
#         else 'null' }}, "duration": {{ state_attr("media_player.family_room_tv",
#         "media_duration") if state_attr("media_player.family_room_tv",
#         "media_duration") is not none else 'null' }}, "updated_at": "{{
#         state_attr('media_player.family_room_tv', 'media_position_updated_at')
#         or "" }}" }
# mode: single

from .resolver import DataResolver
from aiomqtt import Client, Message
from dataclasses import dataclass
from enum import Enum, auto
from mqtt import MqttMessageReceiver
import json
import datetime
import pytz

class MediaPlayerState(Enum):
    UNKNOWN = auto()
    PLAYING = auto()
    BUFFERING = auto()
    IDLE = auto()
    OFF = auto()

@dataclass
class MediaPlayerInformation:
    state: MediaPlayerState
    updated_at: datetime.datetime | None
    media_position: float | None # seconds
    media_duration: float | None # seconds

    # The current media position is either the media_position (most states), or if playing, it's the last known
    # media position plus the time since the last update.
    @property
    def current_media_position(self) -> float | None:
        if self.state != MediaPlayerState.PLAYING:
            return self.media_position
        if self.media_position is None or self.updated_at is None:
            return None
        retval = self.media_position + (datetime.datetime.now(pytz.utc) - self.updated_at).total_seconds()
        return retval

    @property
    def remaining_total_seconds(self) -> float | None:
        if self.media_duration is None or self.current_media_position is None:
            return None
        retval = self.media_duration - self.current_media_position
        if retval < 0:
            return None
        return retval


class MediaPlayerDataResolver(DataResolver[MediaPlayerInformation], MqttMessageReceiver):
    def __init__(self, topic: str) -> None:
        self.data = MediaPlayerInformation(state=MediaPlayerState.UNKNOWN, updated_at=None, media_position=None, media_duration=None)
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

        payload = json.loads(message.payload)
        match payload.get("state"):
            case "playing":
                media_player_state = MediaPlayerState.PLAYING
            case "buffering":
                media_player_state = MediaPlayerState.BUFFERING
            case "idle":
                media_player_state = MediaPlayerState.IDLE
            case "off":
                media_player_state = MediaPlayerState.OFF
            case _:
                media_player_state = MediaPlayerState.UNKNOWN
        self.data = MediaPlayerInformation(
            state=media_player_state,
            updated_at=datetime.datetime.strptime(payload.get("updated_at"), '%Y-%m-%d %H:%M:%S.%f%z'),
            media_position=payload.get("position"),
            media_duration=payload.get("duration"),
        )
        return True
