import sessions
import wx

from core.gui import SquareDialog

class NewSessionDialog (SquareDialog):

 def __init__(self, *args, **kwargs):
  super(NewSessionDialog, self).__init__(title=_("New Session"), *args, **kwargs)
  #First row
  wx.StaticText(parent=self.pane, label=_("Session type:"))
  self.sessions = wx.ListBox(parent=self.pane, choices=self.sessions_list())
  self.sessions.SetSelection(0)
  self.sessions.SetSizerProps(expand=True)
  #Row 2
  wx.StaticText(parent=self.pane, label=_("Session name:"))
  self.name = wx.TextCtrl(parent=self.pane)
  self.name.SetSizerProps(expand=True)
  self.finish_setup()

 def sessions_list (self):
  return sessions.possible_sessions()

