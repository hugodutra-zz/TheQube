import functools
import wx

def always_call_after (method):
 def always_call_after_wrapper (*a, **k):
  try:
   return wx.CallAfter(method, *a, **k)
  except AssertionError:
   pass
 functools.update_wrapper(always_call_after_wrapper, method)
 return always_call_after_wrapper

