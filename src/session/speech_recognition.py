from logger import logger
logging = logger.getChild('core.sessions.speech_recognition')


import config
import output
import wx

from core.sessions.interface.main import Interface
from core.sessions.configuration.configuration import Configuration

class SpeechRecognition (Configuration, Interface):
 def __init__(self, speechmap={}, *args, **kwargs):
  super(SpeechRecognition, self).__init__(*args, **kwargs)
  for i in speechmap.keys():
   speechmap[speechmap[i]] = i
   del(speechmap[i])
  if not self.config.has_key('speechmap'):
   self.config['speechmap'] = {}
  self.speechmap = self.config['speechmap']
  self.update_dict(self.speechmap, speechmap)
  self.speech_module_installed = False
  logging.debug("%s: Speech recognition setup.  Speechmap has %d items." % (self.name, len(self.speechmap.keys())))

 def activate(self):
  if config.main['recognition']['enabled']:
   self.enable_speech_recognition()
  super(SpeechRecognition, self).activate()

 def deactivate (self):
  if self.speech_module_installed and config.main['recognition']['enabled']:
   self.disable_speech_recognition()
  super(SpeechRecognition, self).deactivate()

 def enable_speech_recognition(self):
  if not self.speech_module_installed:
   self.setup_recognition()
  if not self.speech_module_installed:
   output.speak(_("Unable to initialize speech recognition."))
  else:
   self.listener = self.speech_module.listenfor(self.speechmap.keys(), self.process_speech)
   logging.debug("%s: Listening for spoken commands." % self.name)
   config.main['recognition']['enabled'] = True
   config.main.write()

 def disable_speech_recognition(self):
  if self.speech_module_installed:
   self.listener.stoplistening()
   logging.debug("%s: No longer listening for spoken commands." % self.name)
   config.main['recognition']['enabled'] = False
   config.main.write()

 def process_speech (self, phrase, listener):
  logging.debug("%s: Processed phrase %s" % (self.name, phrase))
  if self.speechmap.has_key(phrase):
   func = self.speechmap[phrase]
   try:
    logging.debug("%s: Calling function %s on interface %s" % (self.name, func, self.interface))
    wx.CallAfter(getattr(self.interface, func))
   except:
    logging.exception("%s: Unable to call method %s on interface %s" % (self.name, self.speechmap[phrase], self.interface))
  else:
   logging.debug("%s: phrase %s not found in speechmap %s" % (self.name, phrase, self.speechmap))

 def setup_recognition (self):
  try:
   self.speech_module_installed = True
   import speech
   self.speech_module = __import__('speech')
  except:
   logging.debug("No speech recognition module could be loaded in session %s." % self.name)
   self.speech_module_installed = False
