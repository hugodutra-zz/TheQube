import application
import global_vars
import sys
import wx
import url_shortener
from logger import logger
logging = logger.getChild('config.panels.misc')
from core.gui.configuration import ConfigurationPanel

class MiscPanel (ConfigurationPanel):
 def __init__ (self, *args, **kwargs):
  super(MiscPanel, self).__init__(*args, **kwargs)
  AutoStart_allowed = hasattr(sys, 'frozen') and not global_vars.portable
  self.AutoStart = wx.CheckBox(self, -1, _("Automatically start %s after Windows log on?") % application.name)
  self.AskForExit = wx.CheckBox(self, -1, _("Show confirmation dialog before exiting %s?") % application.name)
  wx.StaticText(parent=self, label=_("Preferred URL Shortener:"))
  self.shorteners = wx.ComboBox(parent=self, choices=url_shortener.list_services(), style = wx.CB_READONLY)
  self.shorteners.SetSizerProps(expand=True)
  wx.StaticText(parent=self, label=_("Preferred audio service:"))
  # M. E.: I don't see why we should not hard-code this list for now
  allAudioServices = ['sndup.net', 'twup.me']
  self.audioServices = wx.ComboBox(parent=self, choices=allAudioServices, style = wx.CB_READONLY)
  self.audioServices.Bind(wx.EVT_COMBOBOX, self.onChange)
  self.audioServices.SetSizerProps(expand=True)
  self.sndupKeySizer = wx.BoxSizer(wx.HORIZONTAL)
  self.sndupKeyLabel = wx.StaticText(parent=self, label=_("Your Sndup.net API Key:"))
  self.sndupKey = wx.TextCtrl(parent=self)
  self.sndupKey.SetSizerProps(expand=True)
  self.sndupKeySizer.Add(self.sndupKeyLabel)
  self.sndupKeySizer.Add(self.sndupKey)
  self.sendMessagesWithEnterKey = wx.CheckBox(self, label=_("Send Messages With Enter Key?"))
  self.stdKeyHandling = wx.CheckBox(self, label=_("Perform standard actions with Home/End keys?"))
  sndupKey_allowed = self.audioServices.GetValue() == "sndup.net"
  logging.debug("@current audio service is {0}, type {1}". format(self.audioServices.GetValue(), type(self.audioServices.GetValue())))
  self._first = self.AutoStart if AutoStart_allowed else self.AskForExit
  if not AutoStart_allowed:
   self.AutoStart.Show(False)
  if not sndupKey_allowed:
   self.sndupKeySizer.ShowItems(False)

  self.finish_setup()

 def onChange(self, ev):
  self.sndupKeySizer.ShowItems(False) if self.audioServices.GetValue() != "sndup.net" else self.sndupKeySizer.ShowItems(True)