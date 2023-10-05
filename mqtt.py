import json
import traceback
import asyncio
from asyncio_mqtt import Client
import backoff
import socket

# MQTT_BROKER = 'mqtt_broker_address'
# MQTT_PORT = 1883
# MQTT_USERNAME = 'your_username'
# MQTT_PASSWORD = 'your_password'
# MQTT_TOPIC_CMD = 'homeassistant/switch/clock/cmd'
# MQTT_TOPIC_STATE = 'homeassistant/switch/clock/state'

@backoff.on_exception(backoff.expo, Exception)  # Catch all exceptions
async def connect_and_listen_mqtt(clock):
    client = Client(
        host=MQTT_BROKER,
        port=MQTT_PORT,
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD
    )

    async with client:
        # Subscribe to the topic where we'll receive commands for the switch
        await client.subscribe(MQTT_TOPIC_CMD)

        async for message in client.filtered_messages(MQTT_TOPIC_CMD):
            cmd = message.payload.decode().upper()

            if cmd == "ON":
                await clock.turn_on()
                await send_status(client, "ON")
            elif cmd == "OFF":
                await clock.turn_off()
                await send_status(client, "OFF")

async def send_status(client, status):
    # Send status updates to the state topic
    await client.publish(MQTT_TOPIC_STATE, status, qos=1)

async def start_mqtt(clock):
    try:
        await connect_and_listen_mqtt(clock)
    except Exception as e:
        print(f"Failed to connect or process messages after retries: {e}")

def config_arg_parser(parser):
    parser.add_argument("--mqtt-host",
        help="MQTT hostname",
        optional=True,
        default=os.environ.get("MQTT_HOST"),
        type=str)
    parser.add_argument("--mqtt-port",
        help="MQTT port",
        optional=True,
        default=os.environ.get("MQTT_PORT",
        1883),
        type=int)
    parser.add_argument("--mqtt-username",
        help="MQTT username",
        optional=True,
        default=os.environ.get("MQTT_USERNAME"),
        type=str)
    parser.add_argument("--mqtt-password",
        help="MQTT password",
        optional=True,
        default=os.environ.get("MQTT_PASSWORD"),
        type=str)
    parser.add_argument(
        "--mqtt-topic-prefix",
        help="MQTT topic prefix",
        optional=True,
        default=os.environ.get("MQTT_TOPIC_PREFIX", f"pixelperfectpi/{socket.gethostname()}/"),
        type=str)
