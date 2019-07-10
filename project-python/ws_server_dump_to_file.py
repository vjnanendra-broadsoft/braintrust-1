#!env/bin/python
# vim: sw=2 ts=2 sts=2 fdm=marker

import asyncio
import websockets
import sys

async def server(websocket, path):
  with open('output.raw', 'ab') as f:
    while True:
      try:
        data = await websocket.recv()
        f.write(data)
      except websockets.ConnectionClosed:
        print("Connection closed")
        break
      except Exception as e:
        print(f"Exception occured: {str(e)}")

def main():
  loop = asyncio.get_event_loop()

  try:
    loop.run_until_complete(websockets.serve(server, '0.0.0.0', 9000))
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    print("finished")
    loop.close()

if __name__ == "__main__":
  sys.exit(main())


