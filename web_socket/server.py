import asyncio

import websockets


async def echo(websocket, path):
    async for message in websocket:
        decoded_message = message.decode("utf-8")
        print(f"Someone said {decoded_message}")

        # await websocket.send(decoded_message)  # Echo back the received message


while True:
    try:
        start_server = websockets.serve(echo, "localhost", 8765, ping_timeout=None)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.ConnectionClosedError():
        continue
    except Exception as e:
        raise e
