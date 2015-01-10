import logging as original_logging
logging = original_logging.getLogger('core.output')

from accessible_output2 import outputs
import config
import sys
import sessions

speaker = None

def speak(text, interrupt=0):
 global speaker
 if not speaker:
  setup()
 speaker.speak(text,interrupt);
 try:
  if config.main['braille']['brailleSpoken'] == True:
   speaker.braille(text)
 except TypeError: #The configuration isn't setup
  pass

def CopyPostToClipboard (buffer=None, index=None):
 if not buffer:
  buffer = sessions.current_session.current_buffer
 if not index and index != 0:
  index = buffer.index
 formatted = buffer.format_item_clipboard(index)
 return Copy(formatted)

def Copy(text):
 #Copies text to the clipboard.
 import win32clipboard
 win32clipboard.OpenClipboard()
 win32clipboard.EmptyClipboard()
 win32clipboard.SetClipboardText(text)
 win32clipboard.CloseClipboard()
 return True

def AnnounceSession(session=None, interrupt=True):
 if not session:
  session = sessions.current_session
 if not session:
  answer = _("No current session.")
 else:
  answer = "%s: %s" % (session.type, session.name)
 speak(answer, interrupt)

def setup ():
 global speaker, brailler
 logging.debug("Initializing output subsystem.")
 try:
  if config.main['speech']['screenreader'] == 'SAPI':
   speaker = outputs.sapi5.SAPI5()
  else:
   speaker = outputs.auto.Auto()
 except:
  return logging.exception("Output: Error during initialization.")
 try:
  if config.main['speech']['screenreader'] == 'SAPI':
   speaker.set_rate(config.main['speech']['rate'])
   speaker.set_volume(config.main['speech']['volume'])
   speaker.set_voice(config.main['speech']['voice'])
 except:
  logging.exception("Unable to set sapi speech properties from configuration")
