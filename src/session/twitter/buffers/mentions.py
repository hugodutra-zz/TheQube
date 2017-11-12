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
  return self.timeline_update(update_function_name='get_mentions_timeline', since_id=self.get_max_twitter_id(), include_rts=True, include_entities=True, tweet_mode='extended')

 def handles_post(self, post):
  if 'full_text' in post and (self.session.username.lower() in [item['screen_name'] for item in post['entities']['user_mentions']] or '@%s' % self.session.username.lower() in post['full_text'].lower()):
   return True
