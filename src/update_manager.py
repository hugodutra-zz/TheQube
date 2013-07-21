from logger import logger
logging = logger.getChild('updater')

import os
import wx
from platform_utils import paths
from gui_components.message_boxes import info_message
import application
import shutdown
import updater
from utils.repeating_timer import RepeatingTimer
from utils.thread_utils import call_threaded
from utils.wx_utils import question_dialog

UPDATE_INTERVAL = 3600 #30 minutes

def check_for_update():
 if not paths.is_frozen():
  return
 url = updater.find_update_url(application.update_url, application.version)
 if url is None:
  return
 new_path = os.path.join(paths.app_data_path(application.name), 'updates', 'update.zip')
 app_updater = updater.AutoUpdater(url, new_path, 'bootstrap.exe', app_path=paths.app_path(), postexecute=paths.executable_path(), finish_callback=update_complete)
 d = question_dialog(parent=application.main_frame, caption=_("Update %s") % application.name, message=_("An update for %s is available, would you like to download and install it now?") % application.name, style=wx.YES|wx.NO|wx.ICON_WARNING)
 if d!= wx.ID_YES:
  return logging.debug("User denied the update request!")
 logging.debug("User requested %s update.  Initialising update process." % application.name)
 app_updater.start_update()



def setup():
 application.update_timer = RepeatingTimer(UPDATE_INTERVAL, check_for_update)
 application.update_timer.start()
 call_threaded(check_for_update)

def update_complete():
 info_message(title=_("The Qube update"), message=_("""An update for The Qube has been downloaded and installed. Press okay to restart the application and begin using the new version.
 Enjoy!"""))
 shutdown.exit()
