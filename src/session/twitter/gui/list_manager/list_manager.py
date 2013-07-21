from logger import logger
logging = logger.getChild('sessions.twitter.gui.list_manager.list_manager')

from . import AddListDialog

import output
import sessions
import wx

from core.gui import SquareDialog

class ListManagerDialog(SquareDialog):

 def __init__(self, screen_name, lists, *args, **kwargs):
  self.index = wx.NOT_FOUND
  self.screen_name = screen_name or sessions.current_session.username
  self.lists = lists
  super(ListManagerDialog, self).__init__(title=_("List manager"), *args, **kwargs)
  self.lists = self.labeled_control(_("Current lists:"), ListsListView, screen_name=screen_name, lists=self.lists)
  self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.changed_selection, self.lists)
  self.Bind(wx.EVT_LIST_DELETE_ITEM, self.DeleteList, self.lists)
  #What can we do with the lists?
  self.add = self.labeled_control(_("&Add list..."), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.NewList, self.add)
  self.edit = self.labeled_control(_("&Edit list..."), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.EditList, self.edit)
  self.remove = self.labeled_control(_("&Remove list..."), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.DeleteList, self.remove)
  self.subscribe = self.labeled_control(_("Subscribe"), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.subscribe)
  self.unsubscribe = self.labeled_control(_("&Unsubscribe"), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.OnUnsubscribe, self.unsubscribe)
  self.spawn = self.labeled_control(_("&Spawn list"), wx.Button)
  self.Bind(wx.EVT_BUTTON, self.SpawnList, self.spawn)
  self.update_mod_buttons()
  self.update_subscribe_buttons()
  self.update_spawn()
  self.finish_setup()

 def create_buttons(self):
  self.btn_close = wx.Button(parent=self.pane, id=wx.ID_CLOSE)
  self.SetEscapeId(wx.ID_CLOSE)
  

 def NewList (self, evt):
  evt.Skip()
  dlg = AddListDialog(parent=self.GetParent(), title=_("Add list"))
  if dlg.ShowModal() != wx.ID_OK:
   dlg.Destroy()
   return output.speak(_("Canceled."), True)
  logging.debug("Retrieving data from add list dialog.")
  name = dlg.name.GetValue()
  mode = dlg.mode.GetStringSelection()
  description = dlg.description.GetValue()
  sessions.current_session.api_call('create_list', action=_("Creating list"), preexec_message=_("Please wait..."), name=name, mode=mode, description=description)
  self.lists.refresh()
  dlg.Destroy()

 def EditList (self, evt):
  evt.Skip()
  which = self.lists.lists[self.lists.GetFocusedItem()]
  dlg = AddListDialog(parent=self.GetParent(), title=_("Edit list"), list=which)
  if dlg.ShowModal() != wx.ID_OK:
   dlg.Destroy()
   return output.speak(_("Canceled."), True)
  logging.debug("Retrieving data from add list dialog.")
  name = dlg.name.GetValue()
  mode = dlg.mode.GetStringSelection()
  description = dlg.description.GetValue()
  sessions.current_session.api_call('update_list', action=_("Editting list"), preexec_message=_("Please wait..."), list_id=which['id'], name=name, mode=mode, description=description)
  self.lists.refresh()
  dlg.Destroy()

 def DeleteList(self, evt):
  evt.Skip()
  which = self.lists.lists[self.lists.GetFocusedItem()]
  d = wx.MessageDialog(self, _("Are you sure you want to delete %s?" % which['name']), _("Delete list"), wx.YES|wx.NO|wx.ICON_WARNING)
  if d.ShowModal() != wx.ID_YES:
   d.Destroy()
   return output.speak(_("Canceled."), True)
  sessions.current_session.api_call('delete_list', action=_("Deleting list %s" % which['name']), preexec_message=_("Please wait..."), list_id=which['id'])
  self.lists.refresh()
  d.Destroy()

 def OnSubscribe(self, evt):
  evt.Skip()
  which = self.lists.lists[self.index]
  sessions.current_session.api_call("subscribe_to_list", action=_("Subscribing to list"), list_id=which['id'])
  self.lists.refresh()

 def OnUnsubscribe(self, evt):
  evt.Skip()
  which = self.lists.lists[self.index]
  sessions.current_session.api_call("unsubscribe_from_list", action=_("Unsubscribing from list"), list_id=which['id'])
  self.lists.refresh()

 def SpawnList(self, evt):
  evt.Skip()
  sessions.current_session.spawn_list_buffer(self.screen_name, self.lists.lists[self.lists.GetFocusedItem()])

 def changed_selection (self, evt):
  evt.Skip()
  self.index = self.lists.GetFocusedItem()
  #set self.screen_name to the owner of the focused list.
  self.screen_name = self.lists.getColumnText(self.index, 1)
  self.update_mod_buttons()
  self.update_subscribe_buttons()
  self.update_spawn()

 def update_mod_buttons(self):
  if self.screen_name is not None and not sessions.current_session.is_current_user(self.screen_name):
   self.edit.Disable()
   self.remove.Disable()
  else:
   self.edit.Enable()
   self.remove.Enable()

 def update_subscribe_buttons(self):
  if sessions.current_session.is_current_user(self.screen_name):
   self.subscribe.Disable()
   self.unsubscribe.Disable()
   return
  if not self.lists.lists[self.index]['following'] and not sessions.current_session.is_current_user(self.screen_name):
   self.subscribe.Enable()
   self.unsubscribe.Disable()
  else:
   self.subscribe.Disable()
   self.unsubscribe.Enable()

 def update_spawn (self):
  if self.index == wx.NOT_FOUND or sessions.current_session.is_list_loaded(self.lists.lists[self.index]):
   self.spawn.Disable()
  else:
   self.spawn.Enable()


class ListsListView (wx.ListView):

 def __init__ (self, screen_name, lists, *args, **kwargs):
  super(ListsListView, self).__init__(*args, **kwargs)
  self.lists = lists
  self.screen_name = screen_name
  #Setup the columns:
  self.InsertColumn(1, _("Name"))
  self.InsertColumn(2, _("Owner"))
  self.InsertColumn(3, _("Mode"))
  self.InsertColumn(4, _("Description"))
  self.refresh()

 def getColumnText(self, index, col):
  item = self.GetItem(index, col)
  return item.GetText()

 def refresh (self):
  self.DeleteAllItems()
  #We can't use self.session here, so use sessions.current_session to get around it.
  self.lists = sessions.current_session.retrieve_lists(user=self.screen_name)
  for item in self.lists:
   self.Append((item['name'], item['user']['screen_name'], item['mode'], item['description']))

