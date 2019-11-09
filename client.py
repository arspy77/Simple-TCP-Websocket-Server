#!/usr/bin/env python

# WS client example

import asyncio
import websockets
import time
import hashlib

async def hello():
    uri = "ws://f3439234.ngrok.io"
    uri = "ws://localhost:12000"
    async with websockets.connect(uri) as websocket:
        # name = input("What's your name? ")

        await websocket.send("!echo ABCabc")
        # print(f"> {name}")

        greeting = await websocket.recv()
        time.sleep(5)
        print(f"< {greeting}")

        await websocket.send("!submission")
        # print(f"> {name}")

        greeting = await websocket.recv()
        fileA = open("teste.zip",'wb')
        fileA.write(greeting)
        fileA.close()
        time.sleep(5)
        
        
        
        
        await websocket.send("!check " + hashlib.md5(greeting).hexdigest())
        # print(f"> {name}")

        greeting = await websocket.recv()
        time.sleep(5)
        print(f"< {greeting}")
        

asyncio.get_event_loop().run_until_complete(hello())

