import global_vars
import wx


class ConfigurationDialog (wx.Dialog):
 def __init__(self, parent, id, *args, **kwargs):
  if 'title' not in kwargs.keys():
   kwargs['title'] = _("Configuration")
  if 'style' not in kwargs.keys():
   kwargs['style'] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
  super(ConfigurationDialog, self).__init__(parent, id, *args, **kwargs)
  parent.Raise()
  self.nb = wx.Notebook(self, wx.ID_ANY, style=wx.BK_DEFAULT)

 def finish_setup(self, focus=None):
  #A sizer to manage the notebook.
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.sizer.Add(self.nb, border=20,flag=wx.LEFT|wx.RIGHT|wx.TOP)
  buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
  self.sizer.Add(buttons,border=20,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)
  self.sizer.Fit(self)
  self.sizer.Hide(buttons)
  self.SetSizer(self.sizer)
  # a little trick to make sure that you can't resize the dialog to less screen space than the controls need
  self.Fit()
  self.SetMinSize(self.GetSize())
  self.SetFocus()
  if focus:
   focus.SetFocus()
