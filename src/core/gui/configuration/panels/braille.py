from core.gui.configuration import ConfigurationPanel
import wx

class BraillePanel (ConfigurationPanel):
 def __init__(self, *args, **kwargs):
  super(BraillePanel, self).__init__(*args, **kwargs)
  wx.StaticText(self, wx.ID_ANY, _("Braille Output:"))
  self._first = self.braille = wx.CheckBox(self, wx.ID_ANY, _("Braille spoken text?"))
  self.finish_setup()
