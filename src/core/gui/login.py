import wx
import wx.lib.sized_controls as sc

from qube import SquareDialog

class LoginDialog (SquareDialog):
 """A handy generic login dialog."""

 def __init__ (self, session, prompt=None, title="", *args, **kwargs):
  title = '%s: %s ' % (session.name.upper(), title)
  super(LoginDialog, self).__init__(title=title, *args, **kwargs)
  if prompt:
   prompt_panel = sc.SizedPanel(self.pane, -1)
   wx.StaticText(prompt_panel, label=prompt)
  self.username = self.labeled_control(label=_("Username"), control=wx.TextCtrl)
  self.password = self.labeled_control(label=_("Password"), control=wx.TextCtrl, style=wx.TE_PASSWORD)
  self.finish_setup()

 def create_buttons (self):
  button_panel = sc.SizedPanel(self.pane, -1)
  button_panel.SetSizerType("horizontal")
  self.login = wx.Button(button_panel, label="Login", id=wx.ID_OK)
  self.login.SetDefault()
  self.cancel = wx.Button(button_panel, id=wx.ID_CANCEL)
