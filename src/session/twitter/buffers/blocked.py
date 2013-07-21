from logger import logger
logging = logger.getChild('sessions.twitter.buffers.blocked')

from core.sessions.buffers.buffer_defaults import buffer_defaults

import output
import threading
import wx

from users import Users
from core.sessions.buffers.update_type import set_update_type
from core.sessions.buffers.buffers import Buffer

class Blocked(Users):

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  self.item_name = _("blocked user")
  self.item_name_plural = _("blocked users")
  super(Blocked, self).__init__ (*args, **kwargs)
  self.set_flag('updatable', True)
  self.item_name = _("blocked user")
  self.item_name_plural = _("blocked users")
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.cursored_update(update_function_name='list_blocks', screen_name=self.username)['users']

 @set_update_type
 def report_update(self, items, update_type=None, *args, **kwargs):
  msg = _("%s blocked users retrieved.") % len(items)
  super(Blocked, self).report_update(items, msg=msg, update_type=update_type)

 
 @buffer_defaults
 def remove_item(self, index = None):
  item = self[index]
  screen_name = self[index]['screen_name']
  confirmation = wx.MessageDialog(parent=None, caption=_("Unblock"), message=_("Are you sure you wish to unblock %s?") % screen_name, style=wx.YES|wx.NO|wx.CANCEL|wx.ICON_QUESTION)
  confirmation.Raise()
  if confirmation.ShowModal() != wx.ID_YES:
   confirmation.Destroy()
   return output.speak(_("Canceled."), True)
  confirmation.Destroy()
  self.session.api_call('destroy_block', _("unblocking %s") % screen_name, screen_name=screen_name)
  Buffer.remove_item(self, index=index, announce=False)

