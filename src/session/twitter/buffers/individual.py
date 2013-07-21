from logger import logger
logging = logger.getChild('sessions.twitter.buffers.user')

import config
import output
import threading

from tweets import Tweets
from core.sessions.buffers.buffers.dismissable import Dismissable

class Individual(Dismissable, Tweets):

 def __init__ (self, username="", *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  self.username = username
  logging.debug("Creating user timeline buffer for %s" % self.username)
  super(Individual, self).__init__ (*args, **kwargs)
  self.set_flag('temp', True)
  self.item_name = _("tweet from %s") % self.username
  self.item_name_plural = _("tweets from %s") % self.username
  self.store_args({'username':username})
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  timeline = self.paged_update('get_user_timeline', since_id=self.get_max_twitter_id(), screen_name=self.username, include_rts=True, include_entities=True)
  if self.initial_update:
   self.initial_update = False
   if not len(self) and not timeline:
    output.speak("%s has no tweets." % self.name)
  return timeline

 def handles_post(self, post):
  return 'user' in post and 'screen_name' in post['user'] and post['user']['screen_name'].lower() == self.username.lower()
