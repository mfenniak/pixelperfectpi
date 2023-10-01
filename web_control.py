import websockets
import json
import traceback
import asyncio

async def start_server(clock):
    open_sockets = []

    async def handler(websocket):
        open_sockets.append(websocket)
        try:
            while True:
                message_raw = await websocket.recv()
                print(f"recvd {message_raw} on websocket")
                message = json.loads(message_raw)

                cmd = message.get("cmd", None)
                if cmd == "ON":
                    print("Switch ON")
                    await clock.turn_on()
                    resp = { "ok": True }
                elif cmd == "OFF":
                    print("Switch OFF")
                    await clock.turn_off()
                    resp = { "ok": True }
                else:
                    resp = { "err": "Unrecognized cmd" }
                await websocket.send(json.dumps(resp))
        except websockets.exceptions.ConnectionClosedOK:
            pass
        except:
            print("Error on socket")
            traceback.print_exc()
        finally:
            open_sockets.remove(websocket)

    async def status_update(status):
        for websocket in open_sockets:
            await websocket.send(json.dumps({"status": status}))

    await websockets.serve(handler, "", 8080)

    return status_update


# async def test_client():
#     uri = "ws://localhost:8080"
#     async with websockets.connect(uri) as websocket:
#         while True:
#             await websocket.send('{"cmd": "ON"}')
#             resp = await websocket.recv()
#             print(resp)
#             await asyncio.sleep(15)
#             await websocket.send('{"cmd": "OFF"}')
#             resp = await websocket.recv()
#             print(resp)
#             resp = await websocket.recv()
#             print(resp)
#             await asyncio.sleep(15)
