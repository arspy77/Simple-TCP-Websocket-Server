#!/usr/bin/env python

# WS client example

import asyncio
import websockets

async def hello():
    uri = "ws://localhost:12000"
    async with websockets.connect(uri) as websocket:
        # name = input("What's your name? ")

        await websocket.send("!echo hithere")
        # print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

        await websocket.send("!check 1234567890")
        # print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

        await websocket.send("!check 12334567890")
        # print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())

