from logger import logger
logging = logger.getChild('sessions.twitter.buffers.search')

import config
import html_filter
import output
import threading
from utils.thread_utils import call_threaded

from tweets import Tweets
from core.sessions.buffers.buffers import Dismissable

class Search (Dismissable, Tweets):

 def __init__(self, store=False, term="", saved=False, saved_id=0, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Search, self).__init__(*args, **kwargs)
  self.initial_update = True
  self.term = unicode(term)
  self.saved = saved or bool(saved_id)
  self.saved_id = saved_id
  if saved:
    call_threaded(self.create_saved_search)
  self.item_name = _("result for %s") % self.term
  self.item_name_plural = _("results for %s") % self.term
  self.item_sound = self.session.config['sounds']['resultReceived']
  self.default_template = 'search'
  self.store_args({'store':store, 'term':term, 'saved':saved})
  self.set_flag('temp', not store)
  if 'name' in self.item_fields:
   del self.item_fields['name']
  if 'geo' in self.item_fields:
   del self.item_fields['geo']
  #self.set_field('screen_name', _("Screen Name"), 'from_user')
  self.init_done_event.set()

 def shutdown (self, end=False):
  if self.saved and not end:
   call_threaded(self.remove_saved_search)
  return super(Search, self).shutdown(end)

 def create_saved_search(self):
  self.init_done_event.wait()
  self.saved_id = self.session.api_call('create_saved_search', action=_("saving search %s") % self.term, report_success=False, query=self.term)['id']

 def remove_saved_search (self):
  return self.session.api_call('destroy_saved_search', action=_("Destroying saved search %s") % self.term, id=self.saved_id, term=self.term)

 def retrieve_update(self, *args, **kwargs):
  if self.initial_update and self.saved:
   self.initial_update = False
  results = self.timeline_update(update_function_name='search', q=self.term, since_id=self.get_max_twitter_id(), include_entities=True)
  if self.initial_update:
   self.initial_update = False
   if not len(self) and not results:
    output.speak("%s returned no results." % self.name)
  return results

 def process_users(self, items):
  return items
