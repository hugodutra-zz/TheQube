from logger import logger
logging = logger.getChild('sessions.twitter.buffers.followers')

import output
import threading

from users import Users

class Followers (Users):

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  if 'username' not in kwargs or ('is_followers_buffer' in kwargs and kwargs['is_followers_buffer']):
   self.is_followers_buffer = True
   kwargs['is_followers_buffer'] = True
  self.initial_update = True
  self.item_name = _("follower")
  self.item_name_plural = _("followers")
  super(Followers, self).__init__ (*args, **kwargs)
  self.set_flag('updatable', True)
  self.item_name = _("follower")
  self.item_name_plural = _("followers")
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.cursored_update(update_function_name='get_followers_list', screen_name=self.username)['users']
