# -*- coding: utf-8 -*-

import logging as original_logging
logging = original_logging.getLogger('core.sessions')

from pydispatch import dispatcher

import config
import global_vars
import meta_interface
import session
import signals
import output
from utils.thread_utils import call_threaded

sessions = []
current_session = None

def RegisterSession (name, type, *args, **kwargs):
 """Registers session  in sessions list."""
 global current_session
 global sessions
 logging.debug("Sessions: Registering new %s session named %s.  Args: %s kwargs: %s" % (type, name, args, kwargs))
 try:
  new = getattr (session, type) (name=name, type=type, *args, **kwargs)
 except:
  return logging.exception("Unable to initialize an instance of session.%s " % type)
 if SessionExists(new):
  return logging.warning("Suppressed duplicate registration of session %s" % name)
 AddSession (new)
 try:
  call_threaded(dispatcher.send, sender=new, signal=signals.session_created)
 except:
  logging.exception("sessions.RegisterSession: Something errored when the NewSession signal was sent.")
 return sessions.index(new)

def SessionExists(session):
 """Bool True/False if session is currently registered in the sessions list."""
 for item in sessions:
  if item.name == session.name:
   return True
 return False

def AddSession (session):
 """Add session to list.  Accepts a session object and returns its index in the sessions list."""
 global sessions
 logging.info("Adding session %s to global list." % session.name)
 sessions.append(session)
 if session_descriptor(session) not in config.main['sessions']['sessions']:
  config.main['sessions']['sessions'].append(session_descriptor(session))
  config.main.write()
 return sessions.index(session)

def RemoveSession(session, end=False, delete = False):
 """Remove session from global sessions list.  Accepts a session object."""
 global sessions
 logging.info("Removing session %s from global list." % session.name)
 index = GetSessionIndex(session)
 index = index - 1
 if not end:
  SetSession(index)
 try:
  sessions.remove(session)
  config.main['sessions']['sessions'].remove(session_descriptor(session))
  config.main.write()
 except:
  pass
 try:
  call_threaded(session.shutdown, end=end, delete=delete)
 except:
  logging.exception("Error deactivating session...")
 dispatcher.send(sender=session, signal=signals.session_destroyed)
 output.AnnounceSession()

def getSessions():
 global sessions
 return sessions

def SetSession (session):
 global sessions
 global current_session
 if session < 0 and len(sessions)>0:
  session = len(sessions)-1
 elif session >= len(sessions):
  session = 0
 try:
  if session == sessions.index(current_session):
   return current_session
 except:
  pass
 if current_session and current_session.active:
  try:
   current_session.deactivate()
  except:
   logging.exception("Error: cannot deactivate session %s." % current_session.name)
 current_session = sessions[session]
 config.main['sessions']['current'] = session
 config.main.write()
 current_session.activate()
 return current_session

def GetSessionByName (name):
 global sessions
 for item in sessions:
  if item.name == name:
   return item
 return None

def GetSession(session):
 if not session:
  return current_session
 else:
  return sessions[session]

def GetSessionIndex(session=None):
 global sessions
 if not session:
  session = current_session
 try:
  answer = sessions.index(session)
 except:
  logging.exception("Unable to retrieve index for session %s" % session.name)
  answer = 0
 return answer

def shutdown(*args, **kwargs):
 logging.debug("Deactivating sessions.")
 for i in sessions:
  try:
   i.shutdown(*args, **kwargs)
  except:
   logging.exception("Sessions: Error shutting down session %s" % i.name)
   continue

def RegisterDefaultSessions():
 logging.info("Registering default sessions...")
 if config.main['sessions']['sessions']:
  for desc in config.main['sessions']['sessions']:
   logging.debug('desc: %r' % desc)
   SpawnSession(*unpack_descriptor(desc))
  try:
   SetSession(config.main['sessions']['current'])
  except:
   logging.exception("Unable to set session to the current session from config")
 else:
  meta_interface.interface().NewSession()
 if not sessions:
  output.speak(_("There was an error spawning previously-loaded sessions.  Please send your log to The Qube's development staff.  Activating new session dialog."), True)
  meta_interface.interface().NewSession()


def SpawnSession (kind, name, *args, **kwargs):
 logging.debug('SpawnSession: Spawning %r session named %r' % (kind, name))
 global current_session
 global sessions
 try:
  new = RegisterSession(name, kind)
 except:
  return logging.exception("Unable to spawn new session type %r" % kind)
 return new

def session_descriptor (session):
 #Given a session object, returns a way to represent it in a reloadable fassion
  return '%s|%s' % (session.type, session.name)

def unpack_descriptor (desc):
 return desc.split('|')

def setup ():
 global current_session
 logging.debug("Initializing sessions subsystem.")
 RegisterDefaultSessions()
 #Give the session a chance to say anything.
 output.AnnounceSession(interrupt=False)

def rename_session(session, name):
 logging.debug("Renaming session %s to %s." % (session, name))
 old_desc = session_descriptor(session)
 session.rename(name)
 old_ind = config.main['sessions']['sessions'].index(old_desc)
 config.main['sessions']['sessions'].remove(old_desc)
 config.main['sessions']['sessions'].insert(old_ind, session_descriptor(session))
 config.main.write()

def possible_sessions ():
 #Replace when autodiscovery worked out.
 return sorted(['Twitter',
  'Stopwatch'
])

class RenameError(Exception): pass
