from core.gui.configuration import ConfigurationPanel
import sessions
import wx

class SoundPanel (ConfigurationPanel):
 def __init__ (self, *args, **kwargs):
  super(SoundPanel, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self, label=_("Sound pack"))
  self.SoundPack = self._first = wx.ComboBox(parent=self, style=wx.CB_READONLY,)
  self.SoundPack.SetSizerProps(expand=True)
  self.mute = wx.CheckBox(parent=self, label=_("Mute session"))
  #self.check = wx.Button(self, -1, _("check for new soundpacks"))
  self.finish_setup()
