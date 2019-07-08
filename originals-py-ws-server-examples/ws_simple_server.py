#!/usr/bin/env python
# vim: sw=2 ts=2 fdm=marker

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

class SimpleEcho(WebSocket):

  def handleMessage(self):
    # echo message back to client
    # self.sendMessage(self.data)
    print(self.data, 'messagerecived')

  def handleConnected(self):
    print(self.address, 'connected')

  def handleClose(self):
    print(self.address, 'closed')

server = SimpleWebSocketServer('', 9000, SimpleEcho)
server.serveforever()
