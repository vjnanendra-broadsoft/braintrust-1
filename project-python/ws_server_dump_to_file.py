#!env/bin/python
# vim: sw=2 ts=2 sts=2 fdm=marker

import asyncio
import websockets
import struct
import sys

async def server(websocket, path):
  print("Started server")
  with open(sys.argv[1], 'wb') as f:
    while True:
      try:
        print("Await websocket.recv()")
        data = await websocket.recv()
        print(len(data))
        # print(struct.unpack('c'*8192, data))
        f.write(data)
      except websockets.ConnectionClosed:
        print("Connection closed")
        break
      except Exception as e:
        print(f"Exception occured: {str(e)}")

def main():
  loop = asyncio.get_event_loop()

  try:
    print("Starting run until complete")
    loop.run_until_complete(websockets.serve(server, '0.0.0.0', 9000))
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    print("finished")
    loop.close()

if __name__ == "__main__":
  sys.exit(main())


