import core.gui
import global_vars
import sessions
import wx
import wx.lib.sized_controls as sc

class QDM(sc.SizedDialog):
 def __init__(self, parent, id, dictionary):
  sc.SizedDialog.__init__(self, parent, id,"%s dictionary manager" % application.name, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
  sessions.current_session.frame.Raise()
  self.pane = self.GetContentsPane()
  self.pane.SetSizerType("form")
  #First Row
  wx.StaticText(self.pane, -1, _("Dictionary Entries"))
  self.dict = DictionaryListView(parent=self.pane, dictionary=dictionary)
  self.dict.SetSizerProps(expand=True)
  #Row 2
  self.add = wx.Button(self.pane, -1, _("Add..."))
  self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
  #Row 3
  self.delete = wx.Button(self.pane, -1, _("Delete..."))
  self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)

  self.btn_close = wx.Button(self.pane, wx.ID_CLOSE)
  self.SetEscapeId(wx.ID_CLOSE)
  # a little trick to make sure that you can't resize the dialog to
  # less screen space than the controls need
  self.Fit()
  self.SetMinSize(self.GetSize())
#Set focus to the llist of dictionary entries by default.
  self.dict.SetFocus()

 def OnAdd(self, evt):
  evt.Skip()
  dlg = core.gui.qdm.AddEntryDialog(self, wx.ID_ANY)
  dlg.ShowModal()

 def OnDelete(self, evt):
  evt.Skip()
  pass

class DictionaryListView(wx.ListView):
 def __init__(self, dictionary=[], *args, **kwargs):
  super(DictionaryListView, self).__init__(*args, **kwargs)
  #setup the columns.
  self.InsertColumn(1, _("Entry"))
  self.InsertColumn(2, _("Replacement"))
  for item in dictionary:
   self.Append(item.split("|"))
