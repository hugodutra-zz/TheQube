import wx
import wx.lib.sized_controls as sc

#Main configuration panel object
class ConfigurationPanel (sc.SizedPanel):
 def __init__(self, parent_nb, *args, **kwargs):
  self.parent_nb = parent_nb
  super(ConfigurationPanel, self).__init__(parent_nb, *args, **kwargs)
  self.SetSizerType("vertical")

 def finish_setup(self):
  self._first.Bind(wx.EVT_NAVIGATION_KEY, self.navigationKeyPressed)
  self.btn_ok = wx.Button(self, wx.ID_OK)
  self.btn_cancel = wx.Button(self, wx.ID_CANCEL)
  self.btn_cancel.Bind(wx.EVT_SET_FOCUS, self.onFocus)
  self._prev_was_cancel = False

 def navigationKeyPressed(self, evt):
  if evt.GetDirection() and self._prev_was_cancel:
   self._prev_was_cancel = False
   self.parent_nb.SetFocus()
  else:
   self._prev_was_cancel = False
   evt.Skip()

 def onFocus(self, evt):
  self._prev_was_cancel = True
  evt.Skip()
