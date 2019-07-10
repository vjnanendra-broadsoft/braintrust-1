#!env/bin/python
# vim: sw=2 ts=2 sts=2 fdm=marker

from multiprocessing import Process, Queue
from google.cloud import speech

import asyncio
import websockets
import sys
import os
import time
import mylog
import pprint


ENCODING = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16
LANG = 'en-US'

# Google API limitations
STREAMING_LIMIT = 55000

# This is web audio's constant
SAMPLE_RATE = 48000

# Our buffer rate chosen in javascript
CHUNK_SIZE = 4096

class WS_SERVER(object):
  # {{{
  def __init__(self, queue):
    self.queue = queue

  async def server(self, websocket, path):
    count = 0
    while True:
      try:
        data = await websocket.recv()
        self.queue.put(data)
      except websockets.ConnectionClosed:
        break
      except Exception as e:
        print(str(e))

      count = count + 1

  def start(self):
    loop = asyncio.get_event_loop()
    loop.run_until_complete( websockets.serve(self.server, '0.0.0.0', 9000) )
    loop.run_forever()
    # }}}

class TRANSCODER(object):
  def __init__(self, queue):
    # {{{
    self.queue = queue
    # }}}

  def generator(self):
    # {{{
    while True:
      chunk = self.queue.get()
      yield chunk
    # }}}

  def start(self):
    # {{{

    print("Waiting for incoming data")
    while self.queue.empty():
      pass

    while True:
      with open('output.raw', 'wb') as f:
        for i in self.generator():
          print("writing chunk of data to file")
          f.write(i)
      # }}}


def main():

  shared_q = Queue()

  ws_server = WS_SERVER(shared_q)
  tr = TRANSCODER(shared_q)

  wsp = Process(target = ws_server.start, name = 'wsp')
  wsp.start()

  tr = Process(target = tr.start, name = 'tr')
  tr.start()

  try:
    wsp.join()
    tr.join()
  except KeyboardInterrupt:
    wsp.terminate()


if __name__ == "__main__":
  sys.exit(main())
