from logger import logger
logging = logger.getChild('sessions.stopwatch.buffers.countdowns')

import misc
import time
from core.sessions.buffers.buffer_defaults import buffer_defaults

from main import Time

class Countdowns(Time):

 def __init__(self, *args, **kwargs):
  super(Countdowns, self).__init__(*args, **kwargs)
  self.default_template = 'countdown'
  self.set_field('remaining', _("Remaining time"), self.get_remaining)

 def get_remaining(self, item):
  return misc.SecondsToString(item.remaining_time(), 1)

 def getStorage (self):
  return self.session.countdowns

 storage = property(fget=getStorage)
