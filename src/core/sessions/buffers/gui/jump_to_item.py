import wx
from wx.lib.intctrl import IntCtrl

from core.gui import SquareDialog

class JumpToPostDialog (SquareDialog):
 def __init__(self, buffer=None, *args, **kwargs):
  super(JumpToPostDialog, self).__init__(title=_("Jump to Item in %s" %buffer.display_name), *args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Enter item number to jump to, 1 to %s:") % str(len(buffer)))
  self.number = IntCtrl(parent=self.pane)
  self.number.SetValue(int(len(buffer) - buffer.index))
  self.number.SetSizerProps(expand=True)
  self.finish_setup()
