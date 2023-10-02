import websockets
import json
import asyncio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, required=True)
parser.add_argument("--check", type=bool)
parser.add_argument("--on", type=bool)
parser.add_argument("--off", type=bool)
parser.add_argument("--monitor", type=bool)

args = parser.parse_args()

async def test_check(host):
    uri = f"ws://{host}:8080"
    async with websockets.connect(uri) as websocket:
        msg = json.loads(await websocket.recv())
        print(repr(msg))

async def send_cmd(host, cmd):
    uri = f"ws://{host}:8080"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({ "cmd_id": 123, "cmd": cmd }))
        while True:
            msg = json.loads(await websocket.recv())
            if msg.get("cmd_id") == 123:
                print("Response: ", msg)
                break

async def monitor(host):
    uri = f"ws://{host}:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = json.loads(await websocket.recv())
            print(repr(msg))

task = None
if args.on == True:
    task = send_cmd(args.host, "ON")
elif args.off == True:
    task = send_cmd(args.host, "OFF")
elif args.monitor == True:
    task = monitor(args.host)
else:
    task = test_check(args.host)

asyncio.run(task)
