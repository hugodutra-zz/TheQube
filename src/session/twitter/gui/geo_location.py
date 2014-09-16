from logger import logger
logging = logger.getChild("sessions.twitter.gui.geo_location")

import wx

from core.gui import SquareDialog

class GeoLocationDialog(SquareDialog):

 def __init__ (self, coordinates=None, location=None, *args, **kwargs):
  super(GeoLocationDialog, self).__init__(title=_("Geo Location"), *args, **kwargs)
  size = self.Size
  size[0] = size[0] / 2
  size[1] = -1
  self.coordinates = self.labeled_control(_("Geo location coordinates:"), wx.TextCtrl, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.WANTS_CHARS, value=str(coordinates), size=size)
  self.coordinates.Bind(wx.EVT_CHAR, self.charPressed)
  self.coordinates.SetSizerProps(expand=True)
  #Row 2
  size = self.Size
  size[0] = size[0] / 2
  size[1] = -1
  self.location = self.labeled_control(_("Location:"), wx.TextCtrl, value=location, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.WANTS_CHARS, size=size)
  self.location.Bind(wx.EVT_CHAR, self.charPressed)
  self.location.SetSizerProps(expand=True)
  #close button
  self.btn_close = wx.Button(self.pane, wx.ID_CLOSE)
  self.btn_close.SetSizerProps(expand = True)
  self.SetEscapeId(wx.ID_CLOSE)
  list(self.focusable_controls())[1].SetFocus()
  self.finish_setup(create_buttons=False, set_focus=False)

 def charPressed(self, evt):
  object = evt.GetEventObject()
  key = evt.GetKeyCode()
  modifiers = evt.GetModifiers()
  if key == wx.WXK_HOME and not modifiers:
   object.SetInsertionPoint(0)
  elif key == wx.WXK_END and not modifiers:
   object.SetInsertionPointEnd()
  elif key == wx.WXK_HOME and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), 0)
  elif key == wx.WXK_END and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), len(object.GetValue()))
  elif key == 1 and modifiers == wx.MOD_CONTROL:
   object.SetInsertionPoint(0)
   object.SetSelection(0, len(object.GetValue()))
  else:
   evt.Skip()
