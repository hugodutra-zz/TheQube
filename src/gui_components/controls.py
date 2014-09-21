import wx

class VerticalSlider(wx.Slider):

 def __init__(self, style=0, *args, **kwargs):
  style = style | wx.SL_VERTICAL
  super(VerticalSlider, self).__init__(style=style, *args, **kwargs)

