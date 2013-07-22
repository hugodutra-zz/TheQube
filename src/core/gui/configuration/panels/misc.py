import application
import global_vars
import sys
import wx
import url_shortener

from core.gui.configuration import ConfigurationPanel

class MiscPanel (ConfigurationPanel):
 def __init__ (self, *args, **kwargs):
  super(MiscPanel, self).__init__(*args, **kwargs)
  AutoStart_allowed = hasattr(sys, 'frozen') and not global_vars.portable
  self.AutoStart = wx.CheckBox(self, -1, _("Automatically start %s after Windows log on?") % application.name)
  self.AskForExit = wx.CheckBox(self, -1, _("Show confirmation dialog before exiting %s?") % application.name)
  wx.StaticText(parent=self, label=_("Prefered URL Shortener:"))
  self.shorteners = wx.ComboBox(parent=self, choices=url_shortener.list_services(), style = wx.CB_READONLY)
  self.shorteners.SetSizerProps(expand=True)
  wx.StaticText(parent=self, label=_("Your Sndup.net API Key:"))
  self.SndUpAPIKey = wx.TextCtrl(parent=self)
  self.SndUpAPIKey.SetSizerProps(expand=True)
  self.sendMessagesWithEnterKey = wx.CheckBox(self, label=_("Send Messages With Enter Key?"))
  self.stdKeyHandling = wx.CheckBox(self, label=_("Perform standard actions with Home/End keys?"))
  #self.useGUI = wx.CheckBox(self, -1, _("Use a GUI (graphical user interface)?"))
  self._first = self.AutoStart if AutoStart_allowed else self.AskForExit
  if not AutoStart_allowed:
   self.AutoStart.Show(False)

  self.finish_setup()
