import functools
import output
import wx

def always_call_after (method):
 def always_call_after_wrapper (*a, **k):
  try:
   return wx.CallAfter(method, *a, **k)
  except AssertionError:
   pass
 functools.update_wrapper(always_call_after_wrapper, method)
 return always_call_after_wrapper

def modal_dialog(dialog, *args, **kwargs):
 dlg = dialog(*args, **kwargs)
 if dlg.ShowModal() != wx.ID_OK:
  output.speak(_("Canceled."), True)
  canceled = True
  raise WXDialogCanceled()
 return dlg

def question_dialog(parent=None, style=wx.YES|wx.NO|wx.CANCEL|wx.ICON_QUESTION, *args, **kwargs):
 if parent:
   parent.Raise()
 dlg = wx.MessageDialog(parent=parent, style=style, *args, **kwargs)
 dlg.Raise()
 response = dlg.ShowModal()
 dlg.Destroy()
 return response


class WXUtilException(Exception): pass
class WXDialogCanceled(WXUtilException): pass
