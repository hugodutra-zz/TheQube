from logger import logger
logging = logger.getChild('sessions.twitter.buffers.favorites')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import config
import output
import threading

from tweets import Tweets
from main import Twitter
from core.sessions.buffers.buffers import Dismissable

class Favorites (Dismissable, Tweets):
 """
 Buffer to show all favorited tweets.
 Deleting a tweet from this buffer will actually unfavorite it.
 """
 def __init__(self, username=None, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  if not username:
   username = kwargs['session'].username
   kwargs['maxAPIPerUpdate'] = 100
  self.username = username
  super(Favorites, self).__init__(*args, **kwargs)
  self.item_name = _("favorite")
  self.item_name_plural = _("favorites")
  self.store_args(dict(username=username))
  self.init_done_event.set()
 
 def retrieve_update(self, *args, **kwargs):
  tweets = self.paged_update(update_function_name='get_favorites', since_id=self.get_max_twitter_id(), include_entities=True, screen_name=self.username)
  self.initial_update = False
  return tweets
  
 @buffer_defaults
 def remove_item(self, index = None):
  item = self[index]
  id = self[index]['id']
  super(Twitter, self).remove_item(index)
  try:
   self.session.TwitterApi.destroy_favorite(id = id)
   output.speak(_("Tweet removed from favorites."), 1)
  except:
   logging.exception("Unable to remove from favorites.")
   output.speak(_("Unable to remove tweet from favorites."))
