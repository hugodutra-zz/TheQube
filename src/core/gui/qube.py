from logger import logger
logging = logger.getChild('core.gui.qube')
import output
import sessions

import wx

from gui_components.sized import SizedDialog

class SquareDialog (SizedDialog):

 def __init__(self, session=None, *args, **kwargs):
  super(SquareDialog, self).__init__(*args, **kwargs)
  if session is None:
   session = sessions.current_session
  if getattr(session, 'modifiers_locked', None):
   session.unlock_modifiers()
   output.speak(_("Modifiers unlocked."))

  #We're interested if this dialog closes.
  self.Bind(wx.EVT_CLOSE, self.on_close)

 def on_close(self, evt):
  evt.Skip()
  logging.info("Destroying dialog")
  self.Destroy()
