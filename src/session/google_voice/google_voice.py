from logger import logger
logging = logger.getChild('sessions.google_voice.main')

from utils.wx_utils import always_call_after
from utils.thread_utils import call_threaded

import pygooglevoicepatches #How hacky can we get before the API just screams for replacement?
from googlevoice import Voice
from googlevoice.util import LoginError
from pydispatch import dispatcher

import application
import buffers
import crypt
from core import gui
import global_vars
import output
import sessions
import signals
import threading
import wx

from core.sessions.buffers import Buffers
from core.sessions.hotkey.hotkey import Hotkey
from session import Login
from session import WebService

class GoogleVoice (Buffers, Hotkey, Login, WebService):

 def __init__ (self, *args, **kwargs):
  self.gv = Voice()
  super (GoogleVoice, self).__init__(*args, **kwargs)
  self.login()

 def register_default_buffers (self):
  (_("Sms"), _("Voicemail"), _("Missed"), _("Received"), _("Placed"))
  self.register_buffer("Sms", buffers.Sms, announce=False)
  self.register_buffer("Voicemail", buffers.Voicemail, set_focus=False, announce=False)
  self.register_buffer("Missed", buffers.Missed, set_focus=False, announce=False)
  self.register_buffer("Received", buffers.Received, set_focus=False, announce=False)
  self.register_buffer("Placed", buffers.Placed, set_focus=False, announce=False)

 def do_login(self, *args, **kwargs):
  #self.wait_for_availability(url='https://www.google.com/voice', message=_("Unable to connect to Google Voice.  %s will retry until connection is established.") % application.name)
  try:
   logging.debug("Logging into Google Voice.")
   self.gv.login(email=self.config['credentials']['email'], passwd=crypt.decrypt(self.config['credentials']['passwd']))
  except LoginError:
   logging.exception("%s: Google Voice login failure." % self.name)
   return
  return True

 def login_succeeded (self):
  self.save_config()
  output.speak(_("Logged into Google Voice as %s") % self.config['credentials']['email'])

 def login_failed (self):
  output.speak(_("Unable to Log into Google Voice."))
  self.login_required()

 def is_login_required (self):
  return not self.config['credentials']['email'] or not self.config['credentials']['passwd']

 @always_call_after
 def login_required(self):
  if hasattr(sessions.current_session, 'frame'):
   frame = sessions.current_session.frame
  else:
   frame = self.frame
  dlg = gui.LoginDialog(parent=frame, title=_("Google Voice Login"), prompt=_("Please provide your credentials to login to Google Voice"), session=self)
  if dlg.ShowModal() == wx.ID_OK:
   self.config['credentials']['email'] = dlg.username.GetValue()
   self.config['credentials']['passwd'] = crypt.encrypt(dlg.password.GetValue())
  dlg.Destroy()
  self.complete_login()

 def show_configuration_dialog(self):
  logging.debug("%s: displaying configuration dialog." % self.name)
  try:
   new = gui.configuration.GoogleVoiceConfigDialog(self.frame, wx.ID_ANY, config=self.config)
   new.SetDefaultValues()
   if new.ShowModal() == wx.ID_OK:
    with self.storage_lock:
     new.SetNewConfigValues()
     self.config['isConfigured'] = True
    output.speak(_("Configuration saved."), True)
    dispatcher.send(sender=self, signal=signals.config_saved)
   else:
    logging.debug("User canceled configuration. Exitting.")
    return output.speak(_("Configuration canceled."), True)
  except:
   logging.exception("%s: Unable to setup configuration dialog." % self.name)

 def shutdown (self, *args, **kwargs):
  self.gv.logout()
  super (GoogleVoice, self).shutdown(*args, **kwargs)

 def config_required (self):
  self.show_configuration_dialog()

 def source_numbers(self):
  answer = list()
  phones = self.gv.contacts.folder['phones']
  for p in sorted(phones):
   if '@' not in phones[p]['formattedNumber']:
    answer.append(phones[p]['formattedNumber'])
  return answer

 def unformat_phone_number(self, number):
  """Given a string representation of a phone number, returns a long of the digits"""
  return int(''.join([c for c in number if  ord(c) in xrange(48, 58)]))
