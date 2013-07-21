from core.sessions.buffers.buffer_defaults import buffer_defaults
import output
from .. import pygooglevoicepatches

from core.sessions.buffers.buffers import Messages
from core.sessions.storage.buffers.storage import Storage
from core.sessions.buffers.buffers import Updating

class GoogleVoice(Updating, Messages, Storage):

 primary_key = 'id'

 def __init__(self, *args, **kwargs):
  super(GoogleVoice, self).__init__(*args, **kwargs)
  self.set_flag('temp', False)
  self.set_flag('filterable', True)
  self.set_flag('exportable', True)
  self.set_field('phone_number', _("Phone number"), 'phoneNumber')
  self.set_field('display_number', _("Display phone number"), 'displayNumber')

 @buffer_defaults
 def item_timestamp(self, index=None):
  try:
   return self.standardize_timestamp(self[index]['startTime'])
  except:
   pass

 def process_update(self, update, *args, **kwargs):
  if type(update) == dict:
   update = self.results_dict_to_list(update)
  update.sort(key=lambda d: self.standardize_timestamp(d['startTime']))
  update = self.find_new_data (update)
  return update

 def standardize_timestamp (self, timestamp):
  return float(str(timestamp)[:-3])

 def results_dict_to_list(self, results):
  new = list()
  for item_id in results:
   results[item_id]['id'] = item_id
   new.append(results[item_id])
  return new

 @buffer_defaults
 def interact(self, index=None):
  """Call the number of the current item."""
  output.speak(_("Calling %s") % self[index]['displayNumber'], True)
  self.session.gv.call(self.get_phone_number(index), long(self.session.gv.contacts.folder['phones']['1']['phoneNumber']))

 @buffer_defaults
 def get_phone_number(self, index=None):
  return long(self[index]['phoneNumber'])

 def paged_update(self, folder_name):
  getattr(self.session.gv, folder_name)() #preload html for other things that don't expect pagination.
  PAGE_LENGTH = 10 #How many items per page
  pages = 2
  page_num = 1
  response = dict()
  while page_num <= pages:
   folder = pygooglevoicepatches.fetchfolderpage(self.session.gv, folder_name, page_num)()
   pages = len(folder) / PAGE_LENGTH + len(folder) % PAGE_LENGTH
   response.update(folder['messages'])
   page_num += 1
  return response

