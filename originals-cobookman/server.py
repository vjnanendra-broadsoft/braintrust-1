#!/usr/bin/python3

import asyncio
import websockets
import json
import io
import threading
import queue

from google.cloud import speech
from google.cloud.gapic.speech.v1 import speech_client
from google.cloud.proto.speech.v1 import cloud_speech_pb2

class StreamingRequest(object):
  """A Streaming Request iterable for speech api."""

  def __init__(self, audio_stream, config):
    """Initializes the streaming request obj.

    params:
    audio_stream: An AudioStream obj
    config: The protobuf configuration for api call
    """
    self.audio_stream = audio_stream
    self.config = config
    self.is_first = True

  def __iter__(self):
    return self

  def __next__(self):
    return self.next()

  def next(self):
    """Generate the next gRPC streaming api request."""
    if self.audio_stream.closed:
      return None

    if self.is_first:
      self.is_first = False
      return cloud_speech_pb2.StreamingRecognizeRequest(
              streaming_config=self.config)

    # block until read some data or until stream closed
    data = self.audio_stream.read()
    while not self.audio_stream.closed and len(data) == 0:
      data = self.audio_stream.read()

    return cloud_speech_pb2.StreamingRecognizeRequest(
            audio_content=data)


def results_to_dict(results):
  if results is None:
    return []

  output = []
  for result in results.results:
    r = {}
    r["stability"] = result.stability
    r["is_final"] = False
    if result.is_final:
      r["is_final"] = True

    r["alternatives"] = []
    for alternative in result.alternatives:
      r["alternatives"].append({
          "transcript": alternative.transcript,
          "confidence": alternative.confidence,
      })
    output.append(r)
  return output

class AudioStream(io.BytesIO):
  """Read dumps latest unread written data."""

  def read(self, n=None):
    """Reads up to `n` bytes."""
    if not hasattr(self, "_position"):
        self._position = 0

    self.seek(self._position)
    data = super(AudioStream, self).read(n)
    self._position += len(data)
    return data


class Transcoder(object):
  """Streaming Transcodes chunks of audio to text."""

  def __init__(self, encoding, rate, language):
    self.encoding = encoding
    self.rate = rate
    self.language = language
    self.audio = AudioStream()
    self.results = queue.Queue()

  def start(self):
    """Start up streaming speech call."""
    threading.Thread(target=self._process).start()

  def write(self, data):
    """Send chunk of audio to speech api."""
    self.audio.write(data)

  def get_result(self):
    """Gets a result from the streaming api."""
    try:
      return self.results.get(False)
    except:
      return None

  def _process(self):
    """sets up a streaming speech api request. And streams results into a queue."""
    self.client = speech_client.SpeechClient()
    self.config = cloud_speech_pb2.StreamingRecognitionConfig(
            config=cloud_speech_pb2.RecognitionConfig(
                encoding=self.encoding,
                sample_rate_hertz=self.rate,
                language_code=self.language),
            interim_results=True)

    requests = StreamingRequest(self.audio, self.config)
    streaming_resp = self.client.streaming_recognize(iter(requests))

    # This will block until self.audio is closed...which closes the streaming_recognize req
    for resp in streaming_resp:
      self.results.put(resp)


@asyncio.coroutine
def audioin(websocket, path):

  # First message should be config
  config = yield from websocket.recv()
  if not isinstance(config, str):
    print("ERROR, no config")
    yield from websocket.send(
        json.dumps({"error": "configuration not received as first message"}));
    return;

  config = json.loads(config)
  transcoder = Transcoder(
      encoding=config["format"],
      rate=config["rate"],
      language=config["language"],
  )

  # Start the transcoding
  transcoder.start()

  # Process incoming audio packets
  while True:
    data = yield from websocket.recv()
    transcoder.write(data)

    # Check for messages
    result = transcoder.get_result()
    result_dict= results_to_dict(result)
    result_json = json.dumps(result_dict)
    print(result_dict)
    yield from websocket.send(result_json)


start_server = websockets.serve(audioin, "0.0.0.0", 80)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()