from .distance import DistanceDataResolver, LocationDistance, haversine_distance
from aiomqtt import Client, Message
from unittest.mock import Mock, MagicMock
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
    message.topic = "homeassistant/output/location/mathieu"
    return message

@pytest.mark.asyncio
async def test_subscribe_to_topics_location(mock_client: Mock) -> None:
    resolver = DistanceDataResolver(40.73061, -73.935242, "homeassistant/output/location/mathieu")
    await resolver.subscribe_to_topics(mock_client)
    mock_client.subscribe.assert_called_with(resolver.topic)

@pytest.mark.asyncio
async def test_handle_message_wrong_topic_location(mock_message: Mock, mock_client: Mock) -> None:
    resolver = DistanceDataResolver(40.73061, -73.935242, "homeassistant/output/location/mathieu")
    mock_message.topic = "wrong/topic"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data is not None
    assert resolver.data.distance == 0.0

@pytest.mark.asyncio
async def test_handle_message_non_bytes_payload_location(mock_message: Mock) -> None:
    resolver = DistanceDataResolver(40.73061, -73.935242, "homeassistant/output/location/mathieu")
    mock_message.payload = "not bytes"
    handled = await resolver.handle_message(mock_message)
    assert not handled
    assert resolver.data is not None
    assert resolver.data.distance == 0.0

@pytest.mark.asyncio
async def test_handle_message_valid_payload_missing_location(mock_message: Mock) -> None:
    resolver = DistanceDataResolver(40.73061, -73.935242, "homeassistant/output/location/mathieu")
    mock_message.payload = bytes(json.dumps({}), encoding='utf-8')
    handled = await resolver.handle_message(mock_message)
    assert resolver.data is not None
    assert resolver.data.distance == 0
    assert handled

@pytest.mark.asyncio
async def test_handle_message_valid_payload_location(mock_message: Mock) -> None:
    resolver = DistanceDataResolver(40.73061, -73.935242, "homeassistant/output/location/mathieu")
    mock_message.payload = bytes(json.dumps({
        "latitude": 34.0522,  # Example: Los Angeles
        "longitude": -118.2437
    }), encoding='utf-8')
    handled = await resolver.handle_message(mock_message)
    assert resolver.data is not None
    # Distance between New York and Los Angeles is approximately 3931 km.
    # We're using a simple formula, so we won't expect exact precision. 
    # So, we're just ensuring that the value is within a reasonable range.
    assert 3900 <= resolver.data.distance <= 4000
    assert handled

def test_haversine_distance() -> None:
    # Test between New York (40.730610, -73.935242) and Los Angeles (34.0522, -118.2437)
    # Expected value is roughly 3931 km.
    distance = haversine_distance(40.730610, -73.935242, 34.0522, -118.2437)
    assert 3900 <= distance <= 4000
