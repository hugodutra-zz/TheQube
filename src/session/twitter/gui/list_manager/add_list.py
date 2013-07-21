import wx

from core.gui import SquareDialog

class AddListDialog(SquareDialog):

 def __init__(self, title="", list=None, *args, **kwargs):
  super(AddListDialog, self).__init__(title=title, *args, **kwargs)
  self.list = list
  #First row
  wx.StaticText(parent=self.pane, label=_("List name:"))
  self.name = wx.TextCtrl(parent=self.pane)
  self.name.SetSizerProps(expand=True)
  #Row 2
  self.mode = wx.RadioBox(parent=self.pane, label=_("List mode:"), choices=['public', 'private'])
  self.mode.SetSizerProps(expand=True)
  #Row 3
  wx.StaticText(parent=self.pane, label=_("List description:"))
  self.description = wx.TextCtrl(parent=self.pane)
  self.description.SetSizerProps(expand=True)
  self.InsertValuesInFields()
  self.finish_setup()

 def InsertValuesInFields(self):
  if self.list is None:
   return
  self.name.SetValue(self.list['name'])
  values = ['public', 'private']
  self.mode.SetSelection(values.index(self.list['mode']))
  self.description.SetValue(self.list['description'])
