import sessions
import wx
from core.gui import SquareDialog

class APICountDialog (SquareDialog):

 def __init__ (self, results_per_api=200, *args, **kwargs):
  self.results_per_api = results_per_api
  super(APICountDialog, self).__init__(*args, **kwargs)

 def setup_api_count_choice (self):
  self.retrieveCount = self.labeled_control(_("Posts per update:"), wx.SpinCtrl)
  self.retrieveCount.SetRange(1, self.results_per_api)
  self.retrieveCount.SetValue(self.results_per_api)
  self.retrieveCount.Bind(wx.EVT_TEXT, self.retrieveCountChanged)
  self.retrieveCount.SetSizerProps(expand=True)
  self.maxAPIPerUpdate = self.labeled_control(label=_("Max API calls to use per update (1 API call = {0} tweets)").format([self.results_per_api]), control=wx.SpinCtrl)
  self.maxAPIPerUpdate.SetRange(1, 100)
  self.maxAPIPerUpdate.SetValue(sessions.current_session.config['updates']['maxAPIPerUpdate'])
  if int(self.retrieveCount.GetValue()) != self.results_per_api:
   self.maxAPIPerUpdate.Disable()
  self.maxAPIPerUpdate.SetSizerProps(expand=True)

 def retrieveCountChanged(self, evt):
  evt.Skip()
  self.maxAPIPerUpdate.SetValue(1)
  if int(self.retrieveCount.GetValue()) == self.results_per_api:
   self.maxAPIPerUpdate.Enable()
  else:
   self.maxAPIPerUpdate.Disable()
