from core.gui.configuration import ConfigurationPanel
import wx
import i18n

class MiscPanel (ConfigurationPanel):

 def __init__ (self, *args, **kwargs):
  super(MiscPanel, self).__init__(*args, **kwargs)
  self._first = self.DMSafeMode = wx.CheckBox(parent=self, label=_("Enable DM safe mode"))
  self.confirmRemovePost = wx.CheckBox(parent=self, label=_("Confirm before removing sent tweets and DMs"))
  wx.StaticText(parent=self, label=_("Retweet Style"))
  self.RTStyle = wx.ComboBox(parent=self, style=wx.CB_READONLY)
  self.RTStyle.SetSizerProps(expand=True)
  self.replyToSelf = wx.CheckBox(parent=self, label=_("Allow reply to self"))
  self.WorkOffline = wx.CheckBox(parent=self, label=_("Work offline"))
  self.WorkOffline.Disable()
  self.finish_setup()
