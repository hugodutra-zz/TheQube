from logger import logger
logging = logger.getChild('sessions.twitter.buffers.list')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import config
import output
import sessions

import threading
import wx

from tweets import Tweets
from core.sessions.buffers.buffers import Dismissable

class ListTimeline (Dismissable, Tweets):

 def __init__ (self, owner=None, list=None, *args, **kwargs):
  self.init_done_event = threading.Event()
  if not owner:
   owner = kwargs['session'].username
  self.owner = owner
  self.list = list
  super(ListTimeline, self).__init__ (*args, **kwargs)
  self.store_args({'list':self.list, 'owner':self.owner})
  self.item_name = _("tweet in %s" % self.display_name)
  self.item_name_plural = _("tweets in %s" % self.display_name)
  if 'spoken' not in self.buffer_metadata.keys():
   self.buffer_metadata['spoken'] = self.session.config['templates']['default_template']
  if 'clipboard' not in self.buffer_metadata.keys():
   self.buffer_metadata['clipboard'] = self.buffer_metadata['spoken']
  logging.debug("List timeline %s created with slug %s and owner %s" % (self.name, self.list['slug'], self.owner))
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.paged_update(update_function_name='get_list_statuses', owner_screen_name=self.owner, slug=self.list['slug'], since_id=self.get_max_twitter_id() or 1, include_rts=True, include_entities=True)
