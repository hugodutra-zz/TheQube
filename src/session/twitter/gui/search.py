import wx

from api_count import APICountDialog

class TwitterSearchDialog (APICountDialog):

 def __init__(self, text="", results_per_api=100, *args, **kwargs):
  super(TwitterSearchDialog, self).__init__(*args, **kwargs)
#First Row
  wx.StaticText(parent=self.pane, label=_("Twitter Search:"))
  if not text:
   text=[""]
  self.term = wx.ComboBox(parent=self.pane, value=text[0], choices=text, style=wx.CB_DROPDOWN)
  self.term.SetSizerProps(expand=True)
  self.store = wx.CheckBox(parent=self.pane, label=_("Persistent results"))
  self.store.SetValue(False)
  self.store.SetSizerProps(expand=True)
  self.save = wx.CheckBox(parent=self.pane, label=_("Save Search"))
  self.save.SetSizerProps(expand=True)
  self.setup_api_count_choice()
  self.finish_setup()
