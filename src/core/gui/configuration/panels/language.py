import i18n
import config
import wx

from core.gui.configuration import ConfigurationPanel

class LanguagePanel (ConfigurationPanel):
 def __init__(self, *args, **kwargs):
  super(LanguagePanel, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self, label=_("Language Selection:"))
  self._first = self.language = wx.ComboBox(parent=self, choices=i18n.printable_available_languages(), value=i18n.printable_lang(i18n.available_languages()[config.main['languages']['current']]), style=wx.CB_READONLY|wx.CB_SORT)
  self.language.SetSizerProps(expand=True)
  self.finish_setup()

