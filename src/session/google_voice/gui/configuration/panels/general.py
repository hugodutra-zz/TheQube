from core.gui.configuration import ConfigurationPanel

import core.gui
import sessions
import wx

class GeneralPanel(ConfigurationPanel):
 def __init__(self, *args, **kwargs):
  super(GeneralPanel, self).__init__(*args, **kwargs)
  wx.StaticText(self, -1, _("Email Address"))
  self._first = self.email = wx.TextCtrl(self, wx.ID_ANY)
  self.email.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("Password"))
  self.passwd = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PASSWORD)
  self.passwd.SetSizerProps(expand=True)
  self.finish_setup()
