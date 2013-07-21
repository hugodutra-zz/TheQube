import gui
import output
import wx
from utils.wx_utils import modal_dialog

from meta_interface import MetaInterface
from core.sessions.buffers.buffer_defaults import buffer_defaults
from core.sessions.buffers.interface import BuffersInterface
from core.sessions.hotkey.interface import HotkeyInterface

class GoogleVoiceInterface (HotkeyInterface, BuffersInterface, MetaInterface):

 def newSMS(self):
  dlg = modal_dialog(gui.SMSDialog, parent=self.session.frame, title=_("New SMS"))
  self.session.gv.send_sms(self.session.unformat_phone_number(dlg.selection.GetValue()), dlg.message.GetValue())
  output.speak(_("Sms successfully sent to %s") % dlg.selection.GetValue())

 def call(self):
  dlg = modal_dialog(gui.CallDialog, parent=self.session.frame, title=_("Call Phone"))
  number = int(dlg.number.GetValue())
  if not number:
   output.speak(_("Please enter a phone number to call."), 1)
   return self.call()
  fp_formatted = dlg.forwardingPhone.GetValue()
  if not fp_formatted:
   output.speak(_("Please indicate where the call should be bridged by selecting a forwarding phone number."), 1)
   return self.call()
  if fp_formatted not in self.session.source_numbers():
   return output.speak(_("Error, forwarding phone number not found."), True)
  output.speak(_("Calling: %r") % number, True)
  self.session.gv.call(number, self.session.unformat_phone_number(fp_formatted))
  output.speak(_("Call placed."))

 @buffer_defaults
 def SMSReply(self, buffer=None, index=None, text=""):
  phone_number = str(buffer.get_phone_number(index))
  if not phone_number:
   return output.speak(_("Unable to detect a sender to reply to."), True)
  numbers = [phone_number]
  new = modal_dialog(gui.SMSDialog, parent=self.session.frame, default=phone_number, selection=numbers, title=_("Reply"), text=text)
  self.session.gv.send_sms(new.selection.GetValue(), new.message.GetValue())
  output.speak(_("Reply sent to %s" % new.selection.GetValue()))
  
interface = GoogleVoiceInterface
