from logger import logger
logging = logger.getChild("sessions.google_voice.gui.configuration")

import wx

from crypt import decrypt, encrypt
from core.gui.configuration import ConfigurationDialog

from panels import *

class GoogleVoiceConfigDialog(ConfigurationDialog):
 def __init__(self, *args, **kwargs):
  if kwargs.has_key('config'):
   self.__dict__['config'] = kwargs['config']
   del(kwargs['config'])
  if kwargs.has_key('templates'):
   self.__dict__['templates'] = kwargs['templates']
   del(kwargs['templates'])
  super(GoogleVoiceConfigDialog, self).__init__(*args, **kwargs)
  self.general = GeneralPanel(self.nb)
  self.nb.AddPage(self.general, _("General"))
  self.finish_setup(focus = None)

 def SetDefaultValues(self):
  self.general.email.SetValue(self.config['credentials'].get('email', ''))
  self.general.passwd.SetValue(decrypt(self.config['credentials'].get('passwd', '')))

 def SetNewConfigValues (self):
  logging.debug("Current config: %s" % self.config.keys())
  logging.debug("Saving configuration from dialog.")
  self.config['credentials']['email'] = str(self.general.email.GetValue()) or ''
  logging.info("Email set to: %s" % self.config['credentials']['email'])
  self.config['credentials']['passwd'] = encrypt(str(self.general.passwd.GetValue())) or ''
  logging.info("Passwd set to: %s" % self.config['credentials']['passwd'])
