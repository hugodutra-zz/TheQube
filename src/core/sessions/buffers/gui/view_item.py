import wx

from core.gui import SquareDialog

class ViewItemDialog (SquareDialog):

 def __init__ (self, label="", text="", *args, **kwargs):
  super(ViewItemDialog, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self.pane, label=label)
  self.text = wx.TextCtrl(parent=self.pane, value=unicode(text), style=wx.TE_MULTILINE|wx.TE_READONLY)
  self.finish_setup()

 def create_buttons (self):
  self.btn_close = wx.Button(parent=self.pane, id=wx.ID_CLOSE)
  self.SetEscapeId(wx.ID_CLOSE)
