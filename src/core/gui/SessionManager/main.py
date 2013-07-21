from logger import logger
logging = logger.getChild("core.gui.session_manager")

import config
import global_vars
import meta_interface
import output
import sessions
import wx
from core.gui.qube import SquareDialog

class SessionManagerDialog(SquareDialog):
 def __init__(self, parent, id):
  SizedDialog.__init__(self, parent, id,"Session manager", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
  #First Row
  wx.StaticText(self.pane, -1, _("Sessions:"))
  self.sessions = SessionsListView(parent=self.pane, sessions=config.main['sessions']['sessions'])
  self.sessions.SetSizerProps(expand=True)
  self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnDelete, self.sessions)
  button_panel = sc.SizedPanel(self.pane, -1)
  button_panel.SetSizerType("horizontal")
  self.switch = wx.Button(button_panel, wx.ID_ANY, _("&Switch to"))
  self.Bind(wx.EVT_BUTTON, self.onSwitch, self.switch)
  self.delete = wx.Button(button_panel, wx.ID_ANY, _("&Delete session..."))
  self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
  self.new = wx.Button(button_panel, wx.ID_ANY, _("&New session..."))
  self.Bind(wx.EVT_BUTTON, self.OnNew, self.new)
  self.btn_close = wx.Button(button_panel, wx.ID_CLOSE)
  self.btn_close.SetSizerProps(expand = True)
  self.SetEscapeId(wx.ID_CLOSE)
  self.finish_setup(create_buttons=False)

 def OnNew(self, evt):
  evt.Skip()
  meta_interface.NewSession()

 def OnDelete(self, evt):
  evt.Skip()
  session = sessions.GetSession(self.sessions.GetFocusedItem())
  d = wx.MessageDialog(self, _("Are you sure you want to close session %s?") % session.name, _("Remove session"), wx.YES|wx.NO|wx.ICON_QUESTION)
  if d.ShowModal() == wx.ID_YES:
   sessions.RemoveSession(session)
  else:
   output.speak(_("Canceled."), 1)

 def onSwitch (self, evt):
  evt.Skip()
  sessions.SetSession(self.sessions.GetFocusedItem())

class SessionsListView(wx.ListView):
 def __init__(self, sessions={}, *args, **kwargs):
  super(SessionsListView, self).__init__(*args, **kwargs)
  #Setup the columns:
  self.InsertColumn(1, _("Type"))
  self.InsertColumn(2, _("Name"))
  for session in sessions:
   self.Append(session.split("|"))
