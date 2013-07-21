from logger import logger
logging = logger.getChild('core.buffers.dismissable')

from core.sessions.buffers.buffers.buffer import Buffer

class Dismissable (Buffer):
 """
 Abstract buffer that makes a sound when opened and closed and can be dismissed.
 """

 def __init__ (self, session, *args, **kwargs):
  super(Dismissable, self).__init__(session, *args, **kwargs)
  self.set_flag('deletable', True)
  session.play(session.config['sounds']['newBuffer'])

 def shutdown (self, end=False, *args, **kwargs):
  super(Dismissable, self).shutdown(end, *args, **kwargs)
  if not end:
   self.session.play(self.session.config['sounds']['dismissBuffer'])
