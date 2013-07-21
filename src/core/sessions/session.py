from logger import logger
logging = logger.getChild('core.sessions.session')

import config
import output

from pydispatch import dispatcher
import signals

from core.named_object import NamedObject

class Session (NamedObject):

 def __init__ (self, type=None, *args, **kwargs):
  self.type = type
  self.kind = self.type.lower()
  super(Session, self).__init__(*args, **kwargs)
  dispatcher.connect(self.initialize, signals.session_created, sender=self)
  self.active = 0
  logging.debug("Created new session: %s" % self.name)
  
 def initialize (self, *args, **kwargs):
  try:
   self.finish_initialization()
  except:
   logging.exception("%s: Error finishing initialization." % self.name)
  logging.debug("%s initialized." % self.name)

 def finish_initialization (self, *args, **kwargs):
  pass

 def activate (self):
  #Called when this session is activated, switched to.
  self.active = True
  logging.debug("Activated session %s" % self.name)

 def deactivate (self):
  #Called when this session is deactivated, switched away from.
  self.active = False
  logging.debug("Deactivated session %s" % self.name)

 def shutdown (self, *args, **kwargs):
  logging.debug("Shutting down session %s" % self.name)
  if self.active:
   self.deactivate()

 def rename (self, name):
  self.name = name

 def __str__(self):
  return self.name

 def speak(self, *args, **kwargs):
  if 'honor_mute' in kwargs:
   honor_mute = kwargs['honor_mute']
   del kwargs['honor_mute']
  else:
   honor_mute = True
  if honor_mute and (config.main['sounds']['mute'] or self.config['sounds']['mute']):
   return
  output.speak(*args, **kwargs)
