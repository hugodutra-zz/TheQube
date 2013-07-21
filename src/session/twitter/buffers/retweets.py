from logger import logger
logging = logger.getChild('sessions.twitter.buffers.retweets')

import config
import output
import threading

from tweets import Tweets
from core.sessions.buffers.buffers import Dismissable

class Retweets(Dismissable, Tweets):

 def __init__ (self, method, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.method = method
  self.item_name = _('retweet')
  self.item_name_plural = _('retweets')
  super(Retweets, self).__init__ (*args, **kwargs)
  self.store_args({'method':method})
  self.temp = False
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  if self.method == "retweeted_to_me":
   update_function_name='retweeted_to_me'
  elif self.method == "retweeted_by_me":
   update_function_name = 'retweeted_by_me'
  elif self.method == "retweets_of_me":
   update_function_name = 'retweeted_of_me'
  count = self.count
  if count > 100:
   count = 100
  return self.paged_update(update_function_name=update_function_name, since_id=self.get_max_twitter_id(), respect_count=False, count=count)
