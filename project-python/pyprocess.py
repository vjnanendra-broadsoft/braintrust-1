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


ENCODING = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16
LANG = 'en-US'

# Google API limitations
STREAMING_LIMIT = 55000

# This is web audio's constant
SAMPLE_RATE = 48000

# Our buffer rate chosen in javascript
CHUNK_SIZE = 4096

def get_current_time():
  return int(round(time.time() * 1000))

def listen_print_loop(responses):
    # {{{
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    responses = (r for r in responses if (
            r.results and r.results[0].alternatives))

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        top_alternative = result.alternatives[0]
        transcript = top_alternative.transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            """
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                stream.closed = True
                break
              """
            num_chars_printed = 0
# }}}

class WS_SERVER(object):
  # {{{
  def __init__(self, queue):
    self.queue = queue

  async def server(self, websocket, path):
    count = 0
    while True:
      try:
        data = await websocket.recv()
        # mylog.a.debug("Putting data in")
        self.queue.put(data)
      except websockets.ConnectionClosed:
        mylog.a.debug("Thank you good bye")
        break
      except Exception as e:
        mylog.a.debug(str(e))

      # mylog.a.debug(f"[{count:<5}] data type = {type(data)}")
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
    self.chunks_given = 0
    # }}}

  def generator(self):
    # {{{
    mylog.a.debug("Started in generator")
    chunks_given = 0

    while True:
      if chunks_given > 550:
        break

      chunk = self.queue.get()
      # mylog.a.debug(f"Gave chunk {chunks_given}")
      chunks_given = chunks_given + 1
      yield chunk


    #while True:
    #  mylog.a.debug("entered while true loop")
    #  if get_current_time() - self.start_time > STREAMING_LIMIT:
    #    mylog.a.debug("STREAMING LIMIT ELAPSED")
    #    self.start_time = get_current_time()
    #    break

    #  mylog.a.debug("time limit is good. Blocking on queue get")

    #  # Use a blocking get() to ensure there's at least one chunk of
    #  # data, and stop iteration if the chunk is None, indicating the
    #  # end of the audio stream.
    #  chunk = self.queue.get()
    #  mylog.a.debug("Queue item obtained")

    #  if chunk is None:
    #    mylog.a.debug("CHUNK IS NONE")
    #    return
    #  else:
    #    mylog.a.debug(f"Picked up {type(chunk)} size {len(chunk)}")


    #  data = [chunk]

    #  # Now consume whatever other data's still buffered.
    #  while True:
    #      try:
    #          chunk = self.queue.get(block=False)
    #          if chunk is None:
    #              return
    #          data.append(chunk)
    #      except self.queue.Empty:
    #          break

    #  yield b''.join(data)
        # }}}

  def start(self):
    # {{{
    self.start_time = get_current_time()
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

    while self.queue.empty():
      pass

    while True:
      mylog.a.debug("Starting while True in transcoder")

      audio_generator = self.generator()

      mylog.a.debug("created audio_generator object")

      requests = (speech.types.StreamingRecognizeRequest(audio_content=content)
          for content in audio_generator)

      mylog.a.debug("created requests object")

      responses = client.streaming_recognize(streaming_config, requests)

      mylog.a.debug("calling listen_print_loop")
      listen_print_loop(responses)

      # }}}


def main():
  mylog.a = mylog.mylog()
  mylog.a.init()
  mylog.a.add_stdout(fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")
  mylog.a.add_file(filepath = 'output.log', fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")

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
