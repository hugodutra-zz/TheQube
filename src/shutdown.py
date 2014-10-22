import logging as original_logging
logging = original_logging.getLogger('core.shutdown')

from pydispatch import dispatcher

import application
import config
import global_vars
import gui
import output
import sessions
import signals
import wx

def exit():
 logging.debug("Shutting down %s" % application.name)
 dispatcher.send(sender=dispatcher.Anonymous, signal=signals.shutdown)
 sessions.shutdown(end=True)
 if global_vars.from_source or global_vars.remote:
  import remote
  remote.shutdown()
 wx.Exit()
