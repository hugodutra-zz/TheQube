from logger import logger
logging = logger.getChild('core.sessions.http_server')

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import global_vars
import threading
import wx
from utils.thread_utils import call_threaded

from core.sessions.interface.main import Interface

class HttpServer (Interface):
 """Class which implements an http server for control of this session. 
 Handles authentication, key-based access, and other metatasks related to providing control."""

 def __init__(self, port=0, urlmap={}, *args, **kwargs):
  super(HttpServer, self).__init__(*args, **kwargs)
  if not hasattr(global_vars, 'http_lock'):
   global_vars.http_lock = threading.RLock()
  if not port:
   port = 7948 #qwit
  self.__host_ = '127.0.0.1'
  self.__port_ = port
  if not urlmap:
   urlmap = {'interface': self.interface}
  self.urlmap = urlmap
  self.handler = Handler
  self.handler.session = self
  self.server = HTTPServer((self.__host_, self.__port_), self.handler)
  logging.debug("%s: Http server setup to listen on http://%s:%d" % (self.name, self.__host_, self.__port_))

 def activate (self, *args, **kwargs):
  self.listen()
  super(HttpServer, self).activate(*args, **kwargs)

 def deactivate(self, *args, **kwargs):
  self.unlisten()
  super(HttpServer, self).deactivate(*args, **kwargs)

 def listen (self):
  call_threaded(self._listen)

 def _listen (self):
  with global_vars.http_lock:
   logging.debug("%s: Http server attempting to listen." % self.name)
   try:
    self.server.serve_forever()
   except:
    logging.exception("%s: http server: unable to listen on port %d" % (self.name, self.port))

 def unlisten (self):
  call_threaded(self._unlisten)

 def _unlisten (self):
  self.server.shutdown()
  logging.debug("%s: Http server no longer listening." % self.name)

 def process_command (self, command, kws={}):
  #Given a command and keywords from the handler, actually calls the appropriate command from the interface.
  basepath, func = command
  if basepath in self.urlmap:
   logging.debug("%s: Base path %s found in URL map." % (self.name, basepath))
   call_threaded(self._exec_command, basepath, func, kws)

 def _exec_command (self, basepath, func, kws):
  logging.debug("Executing command %s from base path: %s with keyword arguments: %r" % (func, basepath, kws))
  try:
   wx.CallAfter(getattr(self.urlmap[basepath], func), **kws)
  except:
   logging.exception("Unable to call command from http server.")

class Handler (BaseHTTPRequestHandler):

 def do_GET(self):
  command = self.path
  kws = {}
  logging.debug("Command: %r" % command)
  if '?' in command: #The command has arguments
   command = command.split('?')
   logging.debug("Command: %r" % command)
   kws = dict(cgi.parse_qsl(command[1]))
   command = command[0]
   logging.debug("Command: %r" % command)
  command = command[1:].split('/')
  logging.debug("Command: %r" % command)
  self.session.process_command(command, kws)
