from logger import logger
logging = logger.getChild('sessions.twitter.buffers.trends')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import output

from main import Twitter
from core.sessions.buffers.buffers import Dismissable
from core.sessions.buffers.update_type import set_update_type

class Trends (Dismissable, Twitter):

 def __init__ (self, *args, **kwargs):
  super(Trends, self).__init__ (*args, **kwargs)
  self.set_flag('temp', True)
  self.set_flag('exportable', False)
  self.set_flag('fixed_template', True)
  self.item_name = _("trend")
  self.item_name_plural = _("trends")
  self.default_template = 'trend'
  self.clear_fields()
  self.set_field('name', _("Trending item's name"), None)

 @buffer_defaults
 def get_hash_tags (self, index):
  return [self[index]['name']]

 def process_users (self, items):
  return items

 @set_update_type
 def report_update(self, items, update_type=None, *args, **kwargs):
  msg = _("%s updated.") % self.name
  super(Trends, self).report_update(items, msg=msg, update_type=update_type)

 def process_update(self, update, *args, **kwargs):
  update.reverse()
  return update

 @buffer_defaults
 def interact(self, index=None):
  output.speak(_("Search"), True)
  self.session.interface.TwitterSearch()

 def extend(self, items, *args, **kwargs):
  index = self.index
  self.clear()
  super(Trends, self).extend(items)
  self.index = index
