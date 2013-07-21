from core.gui.configuration import ConfigurationPanel
import wx

class NavigationPanel (ConfigurationPanel):
 def __init__ (self, *args, **kwargs):
  super(NavigationPanel, self).__init__(*args, **kwargs)
  wx.StaticText(self, -1, _("Move by percentage amount (as a %)"))
  self._first = self.step = wx.SpinCtrl(self, -1, "")
  self.step.SetRange(1, 20)
  self.step.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("Move by time (defined as hours:minutes) hours"))
  self.timeStepHours = wx.SpinCtrl(self, -1, "")
  self.timeStepHours.SetRange(0, 720)
  self.timeStepHours.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("Move by time (defined as hours:minutes) minutes"))
  self.timeStepMins = wx.SpinCtrl(self, -1, "")
  self.timeStepMins.SetRange(0, 59)
  self.timeStepMins.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("Undo stack size"))
  self.undoStackSize = wx.SpinCtrl(self, -1, "")
  self.undoStackSize.SetRange(10, 1000)
  self.undoStackSize.SetSizerProps(expand=True)
  self.finish_setup()
