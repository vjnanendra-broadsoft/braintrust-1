#!/usr/bin/env python

'''
Start by initializing
from mylog import mylog
mylog.init()
mylog.init(logname = "custom")

Add your end points
mylog.add_stdout(fmt = '[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s', tfmt = "%H:%M:%S")
mylog.add_stderr()
mylog.add_file(filepath = '/path/to/file')

Add with custom formatter
mylog.add_stdout(fmt = '%(message)s', tfmt = "%H:%M:%S")

mylog.debug("This is a debug statement")
mylog.warn("This is a warning")

The advantage of using this is that the alternative would
have been
logging.getLogger("hari").debug("This is a debug statement")

# https://docs.python.org/2/library/logging.html#logrecord-attributes

Example: For aligning and padding/fixed width
'[%(lineno)3d] [%(levelname)-12.8s] - %(message)s'

Example: For millisecond time
[%(asctime)s.%(msecs)03d] [%(lineno)3d] %(message)s
'''

import logging
import sys

DEF_FMT = '[%(asctime)s][%(levelname)s] - %(message)s'
DEF_TFMT = '%Y-%m-%d %H:%M:%S'

class mylog:
  # {{{

  def init(self, logname=__name__, loglevel = logging.DEBUG):
    self.logger = logging.getLogger(logname)
    self.logger.setLevel(loglevel)

    self.debug = self.logger.debug
    self.warn = self.logger.warn
    self.info = self.logger.info
    self.error = self.logger.error
    self.critical = self.logger.critical

  def add_stderr(self, loglevel = logging.DEBUG, fmt = DEF_FMT, tfmt = DEF_TFMT):
    err_hdlr = logging.StreamHandler(sys.stderr)
    err_hdlr.setLevel(loglevel)
    err_hdlr.setFormatter(logging.Formatter(fmt, tfmt))

    self.logger.addHandler(err_hdlr)

  def add_stdout(self, loglevel = logging.DEBUG, fmt = DEF_FMT, tfmt = DEF_TFMT):
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setLevel(loglevel)
    out_hdlr.setFormatter(logging.Formatter(fmt, tfmt))

    self.logger.addHandler(out_hdlr)

  def add_file(self, filepath, fmt = DEF_FMT, tfmt = DEF_TFMT):
    file_hdlr = logging.FileHandler(filepath)
    file_hdlr.setLevel(logging.DEBUG)
    file_hdlr.setFormatter(logging.Formatter(fmt, tfmt))

    self.logger.addHandler(file_hdlr)

  def setLevel(self,loglevel = logging.DEBUG):
    self.logger.setLevel(loglevel)

# }}}


''' ---- Formatter Variables ----
%(asctime)s


%(levelno)s
%(levelname)s

%(filename)s
%(funcName)s
%(lineno)d

%(module)s

%(message)s

%(pathname)s

%(thread)d
%(threadName)s
'''
# vim: sw=2 ts=2 fdm=marker
