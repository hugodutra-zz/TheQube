# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('update_manager')

import os
import sys
import wx
import paths
import application
import shutdown
import updater
from utils.repeating_timer import RepeatingTimer
from utils.thread_utils import call_threaded
from utils.wx_utils import question_dialog

UPDATE_INTERVAL = 1800 #30 minutes

def is_frozen():
 import imp
 return hasattr(sys, 'frozen') or imp.is_frozen("__main__")

def check_for_update():
 if not is_frozen():
  return
 url = updater.find_update_url(application.update_url, application.version)
 if url is None:
  return
 new_path = os.path.join(paths.data_path(application.name), 'updates', 'update.zip')
 app_updater = updater.AutoUpdater(url, new_path, 'bootstrap.exe', app_path=paths.app_path(), postexecute=paths.executable_path(), finish_callback=update_complete)
 d = question_dialog(parent=application.main_frame, caption=_("Update %s") % application.name, message=_("An update for %s is available, would you like to download and install it now?") % application.name, style=wx.YES|wx.NO|wx.ICON_WARNING)
 if d!= wx.ID_YES:
  return logging.warning("User denied the update request!")
 logging.debug("User requested %s update.  Initializing update process." % application.name)
 app_updater.start_update()



def setup():
 application.update_timer = RepeatingTimer(UPDATE_INTERVAL, check_for_update)
 application.update_timer.start()
 call_threaded(check_for_update)

def update_complete():
 wx.MessageBox(caption=_("%s update") % application.name, message=_("An update for %s has been downloaded and installed. Click the OK button to restart the application and begin using the new version.\nEnjoy!") % application.name, style=wx.OK | wx.ICON_INFORMATION)
 shutdown.exit()
