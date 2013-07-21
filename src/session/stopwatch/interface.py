from logger import logger
logging = logger.getChild('sessions.stopwatch.interface')

import output
import gui
from utils.wx_utils import modal_dialog

from core.sessions.buffers.interface import BuffersInterface
from core.sessions.hotkey.interface import HotkeyInterface
from meta_interface import MetaInterface

class StopwatchInterface (BuffersInterface, HotkeyInterface, MetaInterface):

 def CountdownTimer(self):
  """Create a timer to count down from the time specified to 0, at which point you will be notified."""

  dlg = modal_dialog(gui.CountdownDialog, parent=self.session.frame, title=_("Countdown Timer"))
  name = dlg.name.GetValue()
  time = dlg.get_time()
  self.session.create_countdown(name, time)
  output.speak(_("Counting."), True)

interface = StopwatchInterface
