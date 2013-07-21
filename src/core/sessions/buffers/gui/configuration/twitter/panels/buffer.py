from core.gui.configuration import ConfigurationPanel
import wx

class BufferPanel (ConfigurationPanel):
 def __init__ (self, buffer, *args, **kwargs):
  self.buffer = buffer
  self._maxAPIPerUpdate_is_active = True
  super(BufferPanel, self).__init__(*args, **kwargs)
  wx.StaticText(self, -1, _("Update interval (in minutes)"))
  self._first = self.checkInterval = wx.SpinCtrl(self, wx.ID_ANY)
  self.checkInterval.SetRange(0, 1440)
  self.checkInterval.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("Number of posts to download per update"))
  self.retrieveCount = wx.SpinCtrl(self, wx.ID_ANY)
  self.retrieveCount.SetRange(10, 200)
  self.retrieveCount.SetValue(200)
  self.retrieveCount.Bind(wx.EVT_TEXT, self.retrieveCountChanged)
  self.retrieveCount.SetSizerProps(expand=True)
  if buffer and buffer.name.startswith("Search for "):
   wx.StaticText(self, -1, _("Max API calls to use per update (1 API call = 100 results)"))
  else:
   wx.StaticText(self, -1, _("Max API calls to use per update (1 API call = 200 tweets)"))
  self.maxAPIPerUpdate = wx.SpinCtrl(self, wx.ID_ANY)
  self.maxAPIPerUpdate.SetRange(1, 100)
  self.maxAPIPerUpdate.SetValue(1)
  self.maxAPIPerUpdate.SetSizerProps(expand=True)
  self.mute = wx.CheckBox(parent=self, label=_("Mute buffer"))
  # Set differences if this is the default settings panel
  if buffer is None:
   self.applyToAll = wx.CheckBox(parent=self, label=_("Apply settings to all buffers"))
  else:
   self.useDefaultSpoken = wx.CheckBox(parent=self, label=_("Use default spoken template"))
   self.useDefaultSpoken.Bind(wx.EVT_CHECKBOX, self.useDefaultSpoken_changed)
   wx.StaticText(self, -1, _("Spoken template:"))
   self.spoken = wx.TextCtrl(self, -1)
   self.spoken.SetSizerProps(expand=True)
   self.useDefaultClipboard = wx.CheckBox(parent=self, label=_("Use default clipboard template"))
   self.useDefaultClipboard.Bind(wx.EVT_CHECKBOX, self.useDefaultClipboard_changed)
   wx.StaticText(self, -1, _("Clipboard template:"))
   self.clipboard = wx.TextCtrl(self, -1)
   self.clipboard.SetSizerProps(expand=True)
   self.useDefaultSpoken_changed()
   self.useDefaultClipboard_changed()
  if self._maxAPIPerUpdate_is_active and int(self.retrieveCount.GetValue()) != 200:
   self.maxAPIPerUpdate.Disable()
  self.finish_setup()

 def retrieveCountChanged(self, evt):
  evt.Skip()
  self.maxAPIPerUpdate.SetValue(1)
  if self._maxAPIPerUpdate_is_active and int(self.retrieveCount.GetValue()) == 200:
   self.maxAPIPerUpdate.Enable()
  else:
   self.maxAPIPerUpdate.Disable()

 def useDefaultSpoken_changed(self, evt=None):
  if evt is not None: evt.Skip()
  self.spoken.Enable(not self.useDefaultSpoken.GetValue())
 
 def useDefaultClipboard_changed(self, evt=None):
  if evt is not None: evt.Skip()
  self.clipboard.Enable(not self.useDefaultClipboard.GetValue())
