import asyncio
import json
import os
import websockets


async def test_websocket():
    token = os.getenv("TEST_TOKEN")

    if not token:
        print("ERROR: TEST_TOKEN is not set.")
        return

    uri = "ws://127.0.0.1:8000/chat/ws"

    async with websockets.connect(uri) as websocket:

        # Step 1: Authenticate
        await websocket.send(
            json.dumps({
                "token": token
            })
        )

        response = await websocket.recv()

        print("Authentication response:")
        print(response)

        # Step 2: Send chat question
        await websocket.send(
            json.dumps({
                "question": "What time is breakfast served?"
            })
        )

        response = await websocket.recv()

        print("Chat response:")
        print(response)


asyncio.run(test_websocket())