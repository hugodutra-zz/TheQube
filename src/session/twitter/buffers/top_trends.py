from logger import logger
logging = logger.getChild('sessions.twitter.buffers.top_trends')

import output
import threading

from core.sessions.buffers.buffer_defaults import buffer_defaults

from trends import Trends

class TopTrends (Trends):

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  super(TopTrends, self).__init__ (*args, **kwargs)
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.api_call('get_place_trends', _("Retrieving trends"), report_success=False, report_failure=False, id=1)[0]['trends']
