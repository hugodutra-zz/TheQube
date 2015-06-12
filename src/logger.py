# -*- coding: utf-8 -*-

# TheQube logger
# A part of TheQube, an accessible social networking client
# Copyright © TheQube Developers Team, 2014 — 2015

import os
import logging
import logging.handlers
import paths
import sys

class TheQubeFileHandler(logging.handlers.RotatingFileHandler):

 def __init__(self, filename, mode='a', maxBytes=102400, encoding='utf-8', delay=0):
  super(TheQubeFileHandler, self).__init__(filename, mode, maxBytes, 0, encoding, delay)

 def doRollover(self):
  """ Truncates the file. By default the file size is 100 kbytes.
  Implemented as suggested at http://stackoverflow.com/questions/24157278/limit-python-log-file."""

  if self.stream:
   self.stream.close()
  dfn = self.baseFilename + u".1"
  if os.path.exists(dfn):
   os.remove(dfn)
  os.rename(self.baseFilename, dfn)
  os.remove(dfn)
  self.mode = 'w'
  self.stream = self._open()

APP_LOG_FILE = u"TheQube.log"
ERROR_LOG_FILE = u"error.log"
MESSAGE_FORMAT = u"%(asctime)s %(name)s %(levelname)s: %(message)s"
DATE_FORMAT = u"%a %b %d, %Y %H:%M:%S"

formatter = logging.Formatter(MESSAGE_FORMAT, datefmt=DATE_FORMAT)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
oauthlib_log = logging.getLogger("oauthlib")
oauthlib_log.setLevel(logging.WARNING)
server_log = logging.getLogger("BaseHTTPServer")
server_log.setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#handlers

app_handler = TheQubeFileHandler(paths.data_path(APP_LOG_FILE), "w", 102400)
app_handler.setFormatter(formatter)
app_handler.setLevel(logging.DEBUG)
logger.addHandler(app_handler)

error_handler = TheQubeFileHandler(paths.data_path(ERROR_LOG_FILE), "w", 102400)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.WARNING)
logger.addHandler(error_handler)
if not hasattr(sys, 'frozen'):
 console_handler = logging.StreamHandler()
 console_handler.setLevel(logging.ERROR)
 console_handler.setFormatter(formatter)
 logger.addHandler(console_handler)
