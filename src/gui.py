from logger import logger
logging = logger.getChild('core.gui')

import application
import config
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
 application.wx_app = wx.App(redirect=True, useBestVisual=True, filename=paths.data_path('error.log'))
 #Create a default frame for the application
 application.main_frame = wx.Frame(None, wx.ID_ANY, application.name)
 application.main_frame.Center()
 #Capture system shutdown events and shutdown the application.
 application.wx_app.Bind(wx.EVT_END_SESSION, on_end_session)

 """
 # Initializing localization
 lang = config.main['languages']['current']
 try:
  wx_locale = wx.Locale()
 except Exception as le:
  logging.exception("@Unable to set locale: %s" % str(le))
 wx_locale.AddCatalogLookupPathPrefix(paths.locale_path())
 if '_' in lang:
  wx_lang = lang.split('_')[0]
 else:
  wx_lang = lang
 try:
  wx_locale.Init(lang, wx_lang)
 except Exception as e:
  logging.exception("@Unable to initialize WX locale: %s" % str(e))
 """


def on_end_session (evt):
 evt.Skip()
 logging.warning("Received system shutdown event.  Initiating application shutdown.  Don't panic!")
 exit()

