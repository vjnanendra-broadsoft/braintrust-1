#!/usr/bin/env python
# vim: sw=2 ts=2 fdm=marker

# WS server example

import asyncio
import websockets

async def hello(websocket, path):

  name = await websocket.recv()
  print(f"< {name}")

  greeting = f"Hello {name}!"

  await websocket.send(greeting)
  print(f"> {greeting}")

start_server = websockets.serve(hello, '0.0.0.0', 9100)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
