from logger import logger
logging = logger.getChild('session.twitter.buffers.list_members')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import output
import threading
import wx

from users import Users

class ListMembers(Users):
 def __init__(self, owner=None, list=None, *args, **kwargs):
  self.init_done_event = threading.Event()
  if not owner:
   owner = kwargs['session'].username
  self.owner = owner
  self.list = list
  self.initial_update = True
  self.item_name = _("list member")
  self.item_name_plural = _("list members")
  super(ListMembers, self).__init__(*args, **kwargs)
  self.init_done_event.set()

 def update(self, *args, **kwargs):
  self.clear()
  super(ListMembers, self).update(*args, **kwargs)

 def retrieve_update(self, *args, **kwargs):
  return self.cursored_update(update_function_name='get_list_members', owner_screen_name=self.owner, slug=self.list['slug'])['users']

 @buffer_defaults
 def remove_item (self, index=None):
  who = self.get_screen_name(index)
  dlg = wx.MessageDialog(parent=self.session.frame, caption=_("Remove user"), message=_("Are you sure you wish to remove %s from list %s?") % (who, self.list['name']), style=wx.YES|wx.NO|wx.CANCEL|wx.ICON_WARNING)
  self.session.frame.Raise()
  if dlg.ShowModal() != wx.ID_YES:
   return output.speak(_("Canceled."), True)
  self.session.api_call('remove_list_member', action=_("removing %s from list %s.") % (who, self.list['slug']), id=who, slug=self.list['slug'])
