#!/usr/bin/python3
# vim: fdm=marker sw=2 ts=2 sts=2

import asyncio
import websockets
import json
import io
import threading
import queue
import struct

def server(websocket, path):

  # Wait for only 10 messages from websocket client
  count = 0
  while count < 10:
    try:
      data = yield from websocket.recv()
    except Exception as e:
      print(str(e))

    print(f"data len = {len(data)}")
    print(f"data type = {type(data)}")
    print(f"data = {data}")
    print("------------------------")

    print(isinstance(data, bytes))




def main():
  asyncio.get_event_loop().run_until_complete( websockets.serve(server, '0.0.0.0', 9000) )
  asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
  main()
