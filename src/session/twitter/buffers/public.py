from logger import logger
logging = logger.getChild('sessions.twitter.buffers.public')

import output
import threading

from tweets import Tweets
from core.sessions.buffers.buffers import Dismissable
from core.sessions.buffers.update_type import set_update_type

class Public (Dismissable, Tweets):
 """The public timeline."""

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  super(Public, self).__init__(*args, **kwargs)
  self.item_name = _("public tweet")
  self.item_name_plural = _("public tweets")
  self.set_flag('temp', True)
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.api_call('public_timeline', report_success=False, report_failure=False, include_entities=True)

 def process_users(self, items):
  return items

