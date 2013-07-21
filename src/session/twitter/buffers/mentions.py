from logger import logger
logging = logger.getChild('sessions.twitter.buffers.mentions')

import config
import output
import threading

from tweets import Tweets

class Mentions (Tweets):
 """The Mentions buffer"""

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Mentions, self).__init__(*args, **kwargs)
  self.item_name = _("mention")
  self.item_name_plural = _("mentions")
  self.item_sound = self.session.config['sounds']['replyReceived']
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.paged_update(update_function_name='get_mentions_timeline', since_id=self.get_max_twitter_id(), include_rts=True, include_entities=True)

 def handles_post(self, post):
  if 'text' in post and '@%s' % self.session.username.lower() in post['text'].lower():
   return True
