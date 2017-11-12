from logger import logger
logging = logger.getChild('sessions.twitter.buffers.directs')

import config
import output
import sessions
import threading

from tweets import Tweets

class Directs (Tweets):
 rapid_access = ('id',)

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Directs, self).__init__(*args, **kwargs)
  self.item_name = _("direct message")
  self.item_name_plural = _("direct messages")
  self.item_sound = self.session.config['sounds']['dmReceived']
  self.set_field('name', _("Name"), ('sender', 'name'))
  self.set_field('screen_name', _("Screen Name"), ('sender', 'screen_name'))
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.timeline_update(update_function_name='get_direct_messages', since_id=self.get_max_twitter_id(), include_entities=True, full_text=True, tweet_mode='extended')

 def handles_post(self, post):
  if 'direct_message' in post and post['direct_message']['recipient']['screen_name'].lower() == self.session.username.lower():
   return True

 def handle_pushed_item(self, item):
  self.handle_update([item['direct_message']])
