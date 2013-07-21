import sessions
import wx
import wx.lib.sized_controls as sc
from core.gui.qube import SquareDialog

class HotkeyDialog(SquareDialog):

 def __init__(self, *args, **kwargs):
  super(HotkeyDialog, self).__init__(title=_("Keystroke Manager"), *args, **kwargs)
  self.ctrl = wx.CheckBox(self.pane, wx.ID_ANY, _("CTRL"))
  self.win = wx.CheckBox(self.pane, wx.ID_ANY, _("WIN"))
  self.alt = wx.CheckBox(self.pane, wx.ID_ANY, _("ALT"))
  self. shift = wx.CheckBox(self.pane, wx.ID_ANY, _("SHIFT"))
  wx.StaticText(self.pane, wx.ID_ANY, _("Key:"))
  self.key = wx.TextCtrl(self.pane, wx.ID_ANY)

 def get_key (self):
  answer = u""
  if self.ctrl.GetValue():
   answer = u"%scontrol+" % answer
  if self.win.GetValue():
   answer = u"%swin+" % answer
  if self.alt.GetValue():
   answer = u"%salt+" % answer
  if self.shift.GetValue():
   answer = u"%sshift+" % answer
  answer = u"%s%s" % (answer, self.key.GetValue().lower())
  return unicode(answer)

 def set_key (self, key):
  key = key.split('+')
  #Forgive me
  for k in key:
   if k == "control":
    self.ctrl.SetValue(True)
   elif k == "alt":
    self.alt.SetValue(True)
   elif k == "shift":
    self.shift.SetValue(True)
   elif k == "win":
    self.win.SetValue(True)
   else:
    self.key.SetValue(k)

 def possible_keys (self):
  #Return a list of possible keys.
  return sessions.current_session.default_keys


class AddHotkeyDialog (HotkeyDialog):
 def __init__ (self, parent, id, keymap={}, *args, **kwargs):
  super(AddHotkeyDialog, self).__init__(parent, id, *args, **kwargs)
  self.keymap = keymap
  wx.StaticText(self.pane, wx.ID_ANY, _("Function:"))
  self.functions = wx.ListBox(self.pane, wx.ID_ANY, choices=self.get_functions())
  self.finish_setup()

 def get_functions (self):
  answer = []
  for i in dir(sessions.current_session.interface):
   if callable(getattr(sessions.current_session.interface, i)) and not self.keymap.has_key(i):
    answer.append(i)
  return answer

class EditHotkeyDialog (HotkeyDialog):
 def __init__(self, *args, **kwargs):
  super(EditHotkeyDialog, self).__init__(*args, **kwargs)
  self.finish_setup()
