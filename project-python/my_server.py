#!/usr/bin/python3
# vim: fdm=marker sw=2 ts=2 sts=2

import asyncio
import websockets
import json
import io
import threading
import queue
import struct
from mylog import mylog

async def server(websocket, path):

  # Wait for only 10 messages from websocket client
  count = 0
  while True:
    try:
      data = await websocket.recv()
    except websockets.ConnectionClosed:
      mylog.debug("Thank you good bye")
      break
    except Exception as e:
      mylog.debug(str(e))

    mylog.debug(f"[{count:<5}] data type = {type(data)}")
    count = count + 1

def main():
  mylog.init()
  mylog.init()
  mylog.add_stdout(fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")
  mylog.add_file(filepath = 'output.log',
          fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")

  loop = asyncio.get_event_loop()
  try:
    loop.run_until_complete( websockets.serve(server, '0.0.0.0', 9000) )
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  except Exception as e:
    mylog.debug(str(e))
  finally:
    mylog.debug("done")
    loop.close()


if __name__ == "__main__":
  main()
