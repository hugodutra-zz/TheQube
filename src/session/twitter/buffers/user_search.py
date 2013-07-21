from logger import logger
logging = logger.getChild('sessions.twitter.buffers.user_search')

import config
import output
import threading

from users import Users

class UserSearch(Users):

 def __init__ (self, query, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  self.term = query
  super(UserSearch, self).__init__ (*args, **kwargs)
  self.item_name = _("result for %s") % self.term
  self.item_name_plural = _("results for %s") % self.term
  self.item_sound =   self.session.config['sounds']['resultReceived']
  self.store_args({'query':self.term})
  self.set_flag('updatable', True)
  self.buffer_metadata['interval'] = self.session.config['updates']['checkInterval']
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.paged_update('search_users', q=self.term)
