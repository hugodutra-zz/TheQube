from logger import logger
logging = logger.getChild('core.gui')

import application
import os
import paths
from shutdown import exit
import wx

def setup():
 logging.debug("Initializing GUI subsystem.")
 #Create the wx app
 try:
  os.remove(paths.data_path('wx.log'))
 except:
  pass
 application.wx_app = wx.App(redirect=True, useBestVisual=True, filename=paths.data_path('wx.log'))
 #Create a default frame for the application
 application.main_frame = wx.Frame(None, wx.ID_ANY, application.name)
 application.main_frame.Center()
 #Capture system shutdown events and shutdown the application.
 application.wx_app.Bind(wx.EVT_END_SESSION, on_end_session)

def on_end_session (evt):
 evt.Skip()
 logging.warning("Received system shutdown event.  Initiating application shutdown.  Don't panic!")
 exit()

