from logger import logger
logging = logger.getChild('sessions.stopwatch.timers')

import misc
import output
import time

from core.sessions.buffers.buffer_defaults import buffer_defaults

from main import Time

class Timers(Time):

 def __init__(self, *args, **kwargs):
  super(Timers, self).__init__(*args, **kwargs)
  self.default_template = 'timer'
  self.set_field('elapsed', _("Elapsed time"), self.get_elapsed)

 @buffer_defaults
 def get_elapsed (self, item=None):
  return misc.SecondsToString(item.elapsed_time(), 3)

 @buffer_defaults
 def interact(self, index=None):
  if not self[index].running and self[index].start_time:
   self[index].reset()
   self[index].start()
   output.speak(_("Stopwatch reset and counting."), True)
  elif not self[index].running:
   self[index].start()
   output.speak(_("Stopwatch counting."), True)
  else:
   self[index].stop()
   output.speak(_("Stopwatch stopped at %s." % misc.SecondsToString(self[index].elapsed_time(), 3)), True)


 def getStorage (self):
  return self.session.timers

 storage = property(fget=getStorage)
