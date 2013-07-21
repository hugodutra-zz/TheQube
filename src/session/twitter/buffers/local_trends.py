from logger import logger
logging = logger.getChild('sessions.twitter.buffers.local_trends')

import output
import threading

from trends import Trends

class LocalTrends (Trends):

 def __init__ (self, woeid=1, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.woeid = woeid
  self.initial_update = True
  self.item_name = _("local trend")
  self.item_name_plural = _("local trends")
  super(LocalTrends, self).__init__ (*args, **kwargs)
  self.store_args({'woeid':woeid})
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.api_call('get_place_trends', _("Retrieving local trends"), report_success=False, report_failure=False, id=self.woeid)[0]['trends']
