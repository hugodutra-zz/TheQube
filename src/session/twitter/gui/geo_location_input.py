import output
import wx

from core.gui import SquareDialog

class GeoLocationInputDialog (SquareDialog):

 def __init__(self, lat=None, long=None, *args, **kwargs):

  super(GeoLocationInputDialog, self).__init__(title=_("Input Coordinates"), *args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Latitude:"))
  size = self.Size
  size[0] = size[0] / 2
  size[1] = -1
  self.lat = wx.TextCtrl(parent=self.pane, size=size)
  if lat:
   self.lat.SetValue(lat)
  self.lat.SetSizerProps(expand=True)
  #Row 2:  
  wx.StaticText(parent=self.pane, label=_("Longitude:"))
  size[0] = size[0] / 2
  size[1] = -1
  self.long = wx.TextCtrl(parent=self.pane, size=size)
  if long:
   self.long.SetValue(long)
  self.long.SetSizerProps(expand=True)
  self.finish_setup()

 def create_buttons(self):
  self.btn_ok = wx.Button(parent=self.pane, id=wx.ID_OK)
  self.btn_ok.Bind(wx.EVT_BUTTON, self.checkValues)
  self.btn_ok.SetDefault()
  self.cancel = wx.Button(parent=self.pane, id=wx.ID_CANCEL)
  self.SetEscapeId(wx.ID_CANCEL)

 def checkValues(self, evt):
  lat_error = _("Error: Latitude must be a value between negative 90 and positive 90.")
  long_error = _("Error: Longitude must be a value between negative 180 and positive 180.")
  try:
   lat = float(self.lat.GetValue())
  except:
   output.speak(lat_error, 1)
   self.lat.SetSelection(-1, -1)
   self.lat.SetFocus()
   return
  if lat < -90 or lat > 90:
   output.speak(lat_error, 1)
   self.lat.SetSelection(-1, -1)
   self.lat.SetFocus()
   return
  try:
   long = float(self.long.GetValue())
  except:
   output.speak(long_error, 1)
   self.long.SetSelection(-1, -1)
   self.long.SetFocus()
   return
  if long < -180 or long > 180:
   output.speak(long_error, 1)
   self.long.SetSelection(-1, -1)
   self.long.SetFocus()
   return
  evt.Skip()
