from logger import logger
logging = logger.getChild('sessions.twitter.buffers.home')

import threading

from tweets import Tweets

class Home (Tweets):
 """The Home buffer"""

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Home, self).__init__(*args, **kwargs)
  self.item_name = _("tweet")
  self.item_name_plural = _("tweets")
  self.item_sound = self.session.config['sounds']['tweetReceived']
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.timeline_update(update_function_name='get_home_timeline', since_id=self.get_max_twitter_id(), include_rts=True, include_entities=True, tweet_mode='extended')

