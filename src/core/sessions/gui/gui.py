from logger import logger
logging = logger.getChild('sessions.gui.main')

#Graphical session

import wx

from core.sessions.session import Session

class Gui (Session):

 def __init__(self, name=None, *args, **kwargs):
  logging.debug("%s: Creating GUI frame." % name)
  self.frame = wx.Frame(None, wx.ID_ANY, name)
  self.frame.Center()
  super(Gui, self).__init__(name=name, *args, **kwargs)

 def shutdown(self, *args, **kwargs):
  self.deactivate()
  self.frame.Close()
  logging.debug("%s: Destroyed GUI frame." % self.name)
  super(Gui, self).shutdown(*args, **kwargs)

 def deactivate (self):
  for child in self.frame.GetChildren():
   logging.debug("Destroying window: %r" % child.Title)
   wx.CallAfter(child.Destroy)
  super(Gui, self).deactivate()
