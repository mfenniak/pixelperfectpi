import websockets
import json
import traceback
import asyncio

async def start_server(clock):
    open_sockets = []

    async def handler(websocket):
        open_sockets.append(websocket)

        # Send current status on new connection
        await websocket.send(json.dumps({ "event": True, "status": clock.state }))

        try:
            while True:
                message_raw = await websocket.recv()
                message = json.loads(message_raw)

                cmd_id = message.get("cmd_id", None)
                cmd = message.get("cmd", None)
                if cmd == "PING":
                    resp = { "cmd_id": cmd_id, "ok": True }
                elif cmd == "ON":
                    await clock.turn_on()
                    resp = { "cmd_id": cmd_id, "ok": True }
                elif cmd == "OFF":
                    await clock.turn_off()
                    resp = { "cmd_id": cmd_id, "ok": True }
                else:
                    resp = { "cmd_id": cmd_id, "err": "Unrecognized cmd" }
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
            await websocket.send(json.dumps({ "event": True, "status": status }))

    await websockets.serve(handler, "", 8080)

    return status_update
