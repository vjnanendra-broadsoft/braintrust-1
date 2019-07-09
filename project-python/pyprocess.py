#!/usr/bin/env python
# vim: sw=2 ts=2 sts=2

from mylog import mylog
from multiprocessing import Process, Queue
from google.cloud import speech

import asyncio
import websockets
import sys
import os


ENCODING = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16
LANG = 'en-US'

# This is web audio's constant
SAMPLE_RATE = 48000

# Our buffer rate chosen in javascript
CHUNK_SIZE = 4096

class WS_SERVER(object):
  def __init__(self, queue):
    self.queue = queue

  async def server(self, websocket, path):
    count = 0
    while True:
      try:
        data = await websocket.recv()
        self.queue.put(data)
      except websockets.ConnectionClosed:
        mylog.debug("Thank you good bye")
        break
      except Exception as e:
        mylog.debug(str(e))

      mylog.debug(f"[{count:<5}] data type = {type(data)}")
      count = count + 1

  def start(self):
    loop = asyncio.get_event_loop()
    loop.run_until_complete( websockets.serve(self.server, '0.0.0.0', 9000) )
    loop.run_forever()

class TRANSCODER(object):
  def __init__(self, queue):
    self.queue = queue

  def generator(self):
    chunk = self.queue.get()
    if chunk is None:
      mylog.debug("received none chunk")
      return
    else:
      mylog.debug(f"received {len(chunk)} or {type(chunk)}")

  def start(self):
    client = speech.SpeechClient()

    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=LANG,
        max_alternatives=1,
        enable_word_time_offsets=True)

    streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)


def main():
  mylog.init()
  mylog.add_stdout(fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")
  mylog.debug("Came here")

  shared_q = Queue()

  ws_server = WS_SERVER(shared_q)
  tr = TRANSCODER(shared_q)

  wsp = Process(target = ws_server.start, name = 'wsp')
  wsp.start()

  tr = Process(target = tr.start, name = 'tr')
  tr.start()

  try:
    wsp.join()
  except KeyboardInterrupt:
    wsp.terminate()


if __name__ == "__main__":
  sys.exit(main())
