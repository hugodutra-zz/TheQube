from logger import logger
logging = logger.getChild('sessions.hotkey.gui.keystroke_manager')

from copy import deepcopy
from dialog import AddHotkeyDialog, EditHotkeyDialog
import core.gui
import sessions
import wx
import wx.lib.sized_controls as sc

from core.gui import SquareDialog

class KeymapDialog(SquareDialog):

 def __init__(self, *args, **kwargs):
  super(KeymapDialog, self).__init__(title=_("Keystroke Manager"), *args, **kwargs)
  self.keymap = sessions.current_session.keymap
  self.new_keymap = deepcopy(self.keymap)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Keymap:"))
  self.keystrokes = KeymapListView(parent=self.pane, keymap=sessions.current_session.keymap, name=_("Keymap:"))
  self.keystrokes.SetMinSize((360, 160))
  self.keystrokes.SetSizerProps(expand=True)
  self.Bind(wx.EVT_LIST_DELETE_ITEM, self.onDelete, self.keystrokes)
  button_panel = sc.SizedPanel(self.pane, -1)
  button_panel.SetSizerType("horizontal")
  self.execute = wx.Button(parent=button_panel, label=_("E&xecute Function"))
  self.Bind(wx.EVT_BUTTON, self.OnExecute, self.execute)
  self.add = wx.Button(parent=button_panel, label=_("&Add..."))
  self.add.Bind(wx.EVT_BUTTON, self.onAdd)
  self.edit = wx.Button(parent=button_panel, label=_("&Edit..."))
  self.edit.Bind(wx.EVT_BUTTON, self.onEdit)
  self.delete = wx.Button(parent=button_panel, label=_("&Delete..."))
  self.delete.Bind(wx.EVT_BUTTON, self.onDelete)
  self.finish_setup()

 def OnExecute(self, evt):
  evt.Skip()
  func = sorted(self.keystrokes.keymap.keys(), key = lambda a: a.lower())[self.keystrokes.GetFocusedItem()]
  getattr(sessions.current_session.interface, func)()

 def onAdd (self, evt):
  evt.Skip()
  dlg = AddHotkeyDialog(sessions.current_session.frame, wx.ID_ANY, keymap=self.new_keymap)
  if dlg.ShowModal() == wx.ID_OK:
   key = dlg.get_key()
   func = dlg.functions.GetStringSelection()
   if not self.mod_keymap(key, func) == True:
    self.onAdd(evt)

 def onEdit (self, evt):
  evt.Skip()
  dlg = EditHotkeyDialog(sessions.current_session.frame, wx.ID_ANY)
  dlg.set_key(self.keystrokes.keys[self.keystrokes.GetFirstSelected()][1])
  if dlg.ShowModal() == wx.ID_OK:
   key = dlg.get_key()
   func = self.keystrokes.keys[self.keystrokes.GetFocusedItem()][0]
   logging.debug("Func: %r key: %r" % (func, key))
   if not self.mod_keymap(key, func) == True:
    self.onEdit(evt)

 def onDelete (self, evt):
  evt.Skip()
  del(self.new_keymap[self.keystrokes.keys[self.keystrokes.GetFocusedItem()][0]])
  self.keystrokes.update_keymap(self.new_keymap)

 def mod_keymap (self, key, func):
  if key in self.new_keymap.values():
   new = wx.MessageBox(_("The keystroke %s is already in use.  Please choose another.") % key, _("Keystroke in use"), parent=sessions.current_session.frame)
   return False
  else:
   self.new_keymap[func] = key
   self.keystrokes.update_keymap(self.new_keymap)
   return True

class KeymapListView (wx.ListView):
 def __init__ (self, keymap={}, *args, **kwargs):
  super(KeymapListView, self).__init__(*args, **kwargs)
  #Setup the columns:
  self.InsertColumn(1, _("Function"))
  self.InsertColumn(2, _("Keystroke"))
  self.InsertColumn(3, _("Description"))
  self.update_keymap(keymap)

 def update_keymap (self, keymap):
  #Overwrites the current list of keys with a new one from a new keymap.
  self.keymap = keymap
  self.keys = []
  for item in sorted(self.keymap.keys(), key = lambda a: a.lower()):
   self.keys.append((item, keymap[item], sessions.current_session.key_description(item)))
  logging.debug('keys: %r' % self.keys)
  self.DeleteAllItems()
  for item in self.keys:
   self.Append(item)
