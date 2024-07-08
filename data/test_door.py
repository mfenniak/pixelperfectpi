from .door import DoorDataResolver, DoorStatus
from aiomqtt import Client, Message
from unittest.mock import Mock
import datetime
import json
import pytest

# Fixture for mock client
@pytest.fixture
def mock_client() -> Mock:
    return Mock(spec=Client)

# Fixture for mock message
@pytest.fixture
def mock_message() -> Mock:
    message = Mock(spec=Message)
    message.topic = "homeassistant/output/door/garage_door"
    return message

@pytest.mark.asyncio
async def test_subscribe_to_topics_door(mock_client: Mock) -> None:
    topic = "homeassistant/output/door/garage_door"
    resolver = DoorDataResolver(topic)
    await resolver.subscribe_to_topics(mock_client)
    mock_client.subscribe.assert_called_with(topic)

@pytest.mark.asyncio
async def test_handle_message_wrong_topic_door(mock_message: Mock, mock_client: Mock) -> None:
    topic = "homeassistant/output/door/garage_door"
    resolver = DoorDataResolver(topic)
    mock_message.topic = "wrong/topic"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data is not None
    assert resolver.data.status == DoorStatus.UNKNOWN

@pytest.mark.asyncio
async def test_handle_message_non_bytes_payload_door(mock_message: Mock) -> None:
    topic = "homeassistant/output/door/garage_door"
    resolver = DoorDataResolver(topic)
    mock_message.payload = "not bytes"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data is not None
    assert resolver.data.status == DoorStatus.UNKNOWN

@pytest.mark.asyncio
@pytest.mark.parametrize("state, expected_status", [
    ("closed", DoorStatus.CLOSED),
    ("open", DoorStatus.OPEN),
    ("unknown", DoorStatus.UNKNOWN)
])
async def test_handle_message_valid_payload_door(mock_message: Mock, state: str, expected_status: DoorStatus) -> None:
    topic = "homeassistant/output/door/garage_door"
    resolver = DoorDataResolver(topic)
    timestamp_str = '2023-10-10 13:52:55.702056-06:00'
    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f%z')
    mock_message.payload = bytes(json.dumps({
        "timestamp": timestamp_str,
        "state": state
    }), encoding='utf-8')
    handled = await resolver.handle_message(mock_message)
    assert handled
    assert resolver.data is not None
    assert resolver.data.status == expected_status
    assert resolver.data.status_since == timestamp
