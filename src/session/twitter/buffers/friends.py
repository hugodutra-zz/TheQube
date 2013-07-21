from logger import logger
logging = logger.getChild('sessions.twitter.buffers.friends')

import output
import threading

from users import Users
from core.sessions.buffers.update_type import set_update_type

class Friends (Users):

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  if 'username' not in kwargs or ('is_friends_buffer' in kwargs and kwargs['is_friends_buffer']):
   self.is_friends_buffer = True
   kwargs['is_friends_buffer'] = True
  self.initial_update = True
  self.item_name = _("friend")
  self.item_name_plural = _("friends")
  super(Friends, self).__init__ (*args, **kwargs)
  self.set_flag('updatable', True)
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.cursored_update(update_function_name='get_friends_list', screen_name=self.username)['users']
