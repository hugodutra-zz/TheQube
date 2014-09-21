import wx

def error_message(parent=None, title=None, message=None):
 return wx.MessageBox(parent=parent, caption=title, message=message, style=wx.OK | wx.ICON_ERROR)

def info_message(parent=None, title=None, message=None):
 return wx.MessageBox(parent=parent, caption=title, message=message, style=wx.OK | wx.ICON_INFORMATION)

def warning_message(parent=None, title=None, message=None):
 return wx.MessageBox(parent=parent, caption=title, message=message, style=wx.OK | wx.ICON_WARNING)