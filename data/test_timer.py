from .timer import TimerDataResolver, TimerState
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
    message.topic = "homeassistant/output/timer/kitchen"
    return message

@pytest.mark.asyncio
async def test_subscribe_to_topics_timer(mock_client: Mock) -> None:
    topic = "homeassistant/output/timer/kitchen"
    resolver = TimerDataResolver(topic)
    await resolver.subscribe_to_topics(mock_client)
    mock_client.subscribe.assert_called_with(topic)

@pytest.mark.asyncio
async def test_handle_message_wrong_topic_timer(mock_message: Mock) -> None:
    topic = "homeassistant/output/timer/kitchen"
    resolver = TimerDataResolver(topic)
    mock_message.topic = "wrong/topic"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data is not None
    assert resolver.data.state == TimerState.UNKNOWN

@pytest.mark.asyncio
async def test_handle_message_valid_payload_timer_running(mock_message: Mock) -> None:
    topic = "homeassistant/output/timer/kitchen"
    resolver = TimerDataResolver(topic)
    mock_message.payload = bytes(json.dumps({
        "state": "active",
        "finishes_at": "2023-01-01T00:00:00+00:00",
        "duration": "0:18:00",
        "remaining": "0:18:00"
    }), encoding='utf-8')
    
    handled = await resolver.handle_message(mock_message)
    assert handled
    assert resolver.data is not None
    assert resolver.data.state == TimerState.RUNNING
    assert resolver.data.duration == datetime.timedelta(minutes=18)
    assert resolver.data.remaining == datetime.timedelta(minutes=18)
    assert resolver.data.finishes_at == datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)

@pytest.mark.asyncio
async def test_handle_message_valid_payload_timer_paused(mock_message: Mock) -> None:
    topic = "homeassistant/output/timer/kitchen"
    resolver = TimerDataResolver(topic)
    mock_message.payload = bytes(json.dumps({
        "state": "paused",
        "duration": "0:18:00",
        "remaining": "0:09:17"
    }), encoding='utf-8')
    
    handled = await resolver.handle_message(mock_message)
    assert handled
    assert resolver.data is not None
    assert resolver.data.state == TimerState.PAUSED
    assert resolver.data.duration == datetime.timedelta(minutes=18)
    assert resolver.data.remaining == datetime.timedelta(minutes=9, seconds=17)
    assert resolver.data.finishes_at is None

@pytest.mark.asyncio
async def test_handle_message_valid_payload_timer_idle(mock_message: Mock) -> None:
    topic = "homeassistant/output/timer/kitchen"
    resolver = TimerDataResolver(topic)
    mock_message.payload = bytes(json.dumps({
        "state": "idle",
        "duration": "0:18:00",
    }), encoding='utf-8')
    
    handled = await resolver.handle_message(mock_message)
    assert handled
    assert resolver.data is not None
    assert resolver.data.state == TimerState.IDLE
    assert resolver.data.duration == datetime.timedelta(minutes=18)
    assert resolver.data.remaining is None
    assert resolver.data.finishes_at is None
