import wx
import sessions

from core.gui import SquareDialog

class CallDialog (SquareDialog):
 def __init__(self, buffer=None, *args, **kwargs):
  super(CallDialog, self).__init__(*args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Enter phone number to call:") )
  self.number = wx.TextCtrl(parent=self.pane)
  self.number.SetSizerProps(expand=True)
  wx.StaticText(parent=self.pane, label=_("Forwarding Number (where calls are bridged)"))
  self.forwardingPhone = wx.ComboBox(parent=self.pane, choices=sessions.current_session.source_numbers(), style=wx.CB_READONLY)
  self.forwardingPhone.SetSelection(0)
  self.finish_setup()
