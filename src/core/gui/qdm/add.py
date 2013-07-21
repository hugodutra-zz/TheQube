import sessions
import wx

class AddEntryDialog():
 def __init__(self, *args, **kwargs):
  super(AddEntryDialog, self).__init__(*args, **kwargs)
  #First Row
  wx.StaticText(self, -1, _("Entry:"))
  self.entry = wx.TextCtrl(self, -1)
  self.entry.SetSizerProps(expand=True)
  #Row 2
  wx.StaticText(self, -1, _("Replacement:"))
  self.replacement = wx.TextCtrl(self, -1)
  self.replacement.SetSizerProps(expand=True)
  #Row 3
  wx.CheckBox(self, -1, _("Case senative?"))

  #Add dialog buttons.
  self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL))
  # a little trick to make sure that you can't resize the dialog to
  # less screen space than the controls need
  self.Fit()
  self.SetMinSize(self.GetSize())
  #Set focus to the entry field by default.
  self.entry.SetFocus()
