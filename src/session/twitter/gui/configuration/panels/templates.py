from core.gui.configuration import ConfigurationPanel
import misc
import wx

class TemplatesPanel (ConfigurationPanel):
 def __init__(self, session, *args, **kwargs):
  self.session = session
  super(TemplatesPanel, self).__init__(*args, **kwargs)
  #Row 1
  wx.StaticText(self, label=_("New generic buffer template:"))
  self._first = self.default_template = wx.TextCtrl(self)
  self.default_template.SetSizerProps(expand=True)
  #Row 2
  wx.StaticText(self, label=_("New search buffer template:"))
  self.search = wx.TextCtrl(self)
  self.search.SetSizerProps(expand=True)
  #Row 3
  wx.StaticText(self, label=_("New followers/friends buffer template:"))
  self.default_followers_friends = wx.TextCtrl(self)
  self.default_followers_friends.SetSizerProps(expand=True)
  #Row 4
  self.buffer_config = wx.Button(self, wx.ID_ANY, _("Modify Existing Buffer Templates..."))
  self.buffer_config.Bind(wx.EVT_BUTTON, self.ShowBufferConfig)
  #Row 5
  wx.StaticText(self, wx.ID_ANY, _("User info template:"))
  self.user_info = wx.TextCtrl(self, wx.ID_ANY)
  self.user_info.SetSizerProps(expand=True)
  #Row 6
  wx.StaticText(self, wx.ID_ANY, _("Reply template:"))
  self.reply = wx.TextCtrl(self, wx.ID_ANY)
  self.reply.SetSizerProps(expand=True)
  #Row 7
  wx.StaticText(self, wx.ID_ANY, _("Retweet template:"))
  self.retweet = wx.TextCtrl(self, wx.ID_ANY)
  self.retweet.SetSizerProps(expand=True)
  #Help button...
  #self.help = wx.Button(self, wx.ID_ANY, _("Help"))
  #self.Bind(wx.EVT_BUTTON, self.ViewHelp, self.help)
  self.finish_setup()

 def ViewHelp(self, evt):
  evt.Skip()
  misc.open_url_in_browser(application.wx_appPath + "\\documentation\\readme.html")
 
 def ShowBufferConfig(self, evt):
  evt.Skip()
  self.session.interface.BufferConfigDialog()
