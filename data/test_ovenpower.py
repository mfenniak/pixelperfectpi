from .ovenpower import OvenOnDataResolver, OvenStatus, Message
from aiomqtt import Client
from unittest.mock import Mock, patch, MagicMock
import json
import pytest

# This fixture will create a mock client for testing
@pytest.fixture
def mock_client():
    return Mock(spec=Client)

# This fixture will create a mock message for testing
@pytest.fixture
def mock_message():
    message = Mock(spec=Message)
    message.topic = "prometheus/alerts/OvenPoweredOn"
    return message

@pytest.mark.asyncio
async def test_subscribe_to_topics(mock_client):
    resolver = OvenOnDataResolver()
    await resolver.subscribe_to_topics(mock_client)
    mock_client.subscribe.assert_called_with(resolver.topic)

@pytest.mark.asyncio
async def test_handle_message_wrong_topic(mock_message, mock_client):
    resolver = OvenOnDataResolver()
    mock_message.topic = "wrong/topic"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data.status == OvenStatus.UNKNOWN

@pytest.mark.asyncio
async def test_handle_message_non_bytes_payload(mock_message):
    resolver = OvenOnDataResolver()
    mock_message.payload = "not bytes"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data.status == OvenStatus.UNKNOWN

@pytest.mark.asyncio
@pytest.mark.parametrize("alert_status, expected_status", [
    ("firing", OvenStatus.ON),
    ("resolved", OvenStatus.OFF)
])
async def test_handle_message_valid_payload(mock_message, alert_status, expected_status):
    resolver = OvenOnDataResolver()
    mock_message.payload = bytes(json.dumps({"status": alert_status}), encoding='utf-8')
    handled = await resolver.handle_message(mock_message)
    assert handled
    assert resolver.data.status == expected_status
