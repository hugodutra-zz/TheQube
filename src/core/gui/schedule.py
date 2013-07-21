from logger import logger
logging = logger.getChild('core.gui.schedule')

import time
import wx
from gui_components.sized import SizedPanel

from qube import SquareDialog

__all__ = ['ScheduleDialog', 'TimePanel', 'TimeEntryPanel']

class ScheduleDialog(SquareDialog):

 def __init__(self, *args, **kwargs):
  super(ScheduleDialog, self).__init__(*args, **kwargs)
  self.method = self.labeled_control(_("Select scheduling method"), wx.RadioBox, choices=[_("Interval"), _("Time")], callback=self.on_method_change)
  self.current_panel = self.time_panel = TimePanel(parent=self.pane)
  self.time_entry_panel = TimeEntryPanel(parent=self.pane)
  self.time_entry_panel.Disable()
  self.finish_setup()

 def on_method_change(self):
  current = self.method.GetSelection()
  if self.current_panel.Enabled:
   self.current_panel.Disable()
  if current == 0:
   logging.debug("Showing timespan entry panel.")
   self.current_panel = self.time_panel
  elif current == 1:
   logging.debug("Showing time entry panel.")
   self.current_panel = self.time_entry_panel
   self.current_panel.update_time()
  self.current_panel.Enable()
  self.do_fit()

 def get_time(self):
  return self.current_panel.get_time()


class TimePanel(SizedPanel):

 def __init__(self, *args, **kwargs):
  super(TimePanel, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self, label=_("Hours:"))
  self.hours = wx.SpinCtrl(parent=self, max=23)
  wx.StaticText(parent=self, label=_("Minutes:"))
  self.minutes = wx.SpinCtrl(parent=self, max=59)
  wx.StaticText(parent=self, label=_("Seconds:"))  
  self.seconds = wx.SpinCtrl(parent=self, max=59)

 def get_time(self):
  #returns the positive time offset as set in this panel
  return self.hours.GetValue() * 3600 + self.minutes.GetValue() * 60 + self.seconds.GetValue()


class TimeEntryPanel(SizedPanel):

 def __init__(self, *args, **kwargs):
  super(TimeEntryPanel, self).__init__(*args, **kwargs)
  wx.StaticText(parent=self, label=_("Hour:"))
  self.hour = wx.SpinCtrl(parent=self, max=23)
  self.minute = wx.SpinCtrl(parent=self, max=59)

 def update_time(self):
  current_time = time.localtime()
  self.hour.SetValue(current_time.tm_hour)
  self.minute.SetValue(current_time.tm_min)
  logging.debug("Updated time in TimeEntryPanel.")

 def get_time(self):
  current_time = time.localtime()
  h, m, s = current_time.tm_hour, current_time.tm_min, current_time.tm_sec
  h = self.hour.GetValue() - h
  m = self.minute.GetValue() - m
  h = h * 3600
  m = m * 60
  new_time = h + m
  if new_time < 0:
   new_time = 0
  return new_time

