import sessions
import wx

from core.gui import SquareDialog

class CountdownDialog (SquareDialog):
 def __init__(self, *args, **kwargs):
  super(CountdownDialog, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self.pane, label=_("Name:"))
  self.name = wx.TextCtrl(parent=self.pane)
  wx.StaticText(parent=self.pane, label=_("Hours:"))
  self.hours = wx.SpinCtrl(parent=self.pane)
  self.hours.SetValue(sessions.current_session.config['countdown']['hours'])
  wx.StaticText(parent=self.pane, label=_("Minutes:"))
  self.minutes = wx.SpinCtrl(parent=self.pane)
  self.minutes.SetValue(sessions.current_session.config['countdown']['minutes'])
  wx.StaticText(parent=self.pane, label=_("Seconds:"))
  self.seconds = wx.SpinCtrl(parent=self.pane)
  self.seconds.SetValue(sessions.current_session.config['countdown']['seconds'])
  self.finish_setup(set_focus=False)
  self.hours.SetFocus()

 def get_time (self):
  #Returns the time set in the dialog as a long representing total seconds.
  seconds = self.seconds.GetValue()
  seconds += (self.minutes.GetValue() * 60)
  seconds += (self.hours.GetValue() * 3600)
  return seconds
