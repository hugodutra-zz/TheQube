import logging as original_logging
logging = original_logging.getLogger('core.remote')
from twisted.internet import reactor
from twisted.manhole import telnet

from utils.repeating_timer import RepeatingTimer
import global_vars
import sessions
import wx

def create_shell_server ():
 logging.debug('Creating shell server instance')
 factory = telnet.ShellFactory()
 port = reactor.listenTCP(7984, factory)
 factory.namespace = construct_namespace()
 factory.username = 'qwitter'
 factory.password = 'debug'
 logging.debug('Listening on port 7984')
 return port

def catch_up():
 reactor.runUntilCurrent()
 reactor.doIteration(0.1)

def setup():
 global timer
 reactor.callWhenRunning(create_shell_server)
 reactor.startRunning()
 timer = RepeatingTimer(0.01, catch_up, daemon=True)
 timer.start()
 logging.info("Debug terminal initialized.")

def shutdown ():
 global timer
 try:
  timer.stop()
  reactor.stop()
 except:
  return
 logging.info("Debug terminal deactivated.")

def construct_namespace():
 ns = dict(cs=sessions.current_session, sessions=sessions)
 return ns

