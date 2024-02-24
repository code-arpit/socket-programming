import asyncio

import websockets


async def hello():
    uri = "ws://localhost:8765"
    print("-----------------")

    async with websockets.connect(uri, ping_timeout=None) as websocket:
        while True:
            try:
                message = input("Enter your message: ")  # Get user input
                encoded_message = message.encode("utf-8")
                await websocket.send(
                    encoded_message
                )  # Send the user's message to the WebSocket server
                response = await websocket.recv()  # Receive server response
                print(f"Server Response: {response}")  # Print the server response
            except websockets.exceptions.ConnectionClosed():
                continue
            except Exception as e:
                raise e


asyncio.get_event_loop().run_until_complete(hello())
