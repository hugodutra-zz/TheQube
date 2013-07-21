import logging as original_logging
logging = original_logging.getLogger('core.output')

from accessible_output import braille, speech
import config
import sys
import sessions

speaker = brailler = None

def speak(text, interrupt=0):
 global speaker
 if not speaker:
  setup()
 speaker.say(text,interrupt);
 try:
  if config.main['braille']['brailleSpoken'] == True:
   Braille(text)
 except TypeError: #The configuration isn't setup
  pass

def Braille (text, *args, **kwargs):
 #Braille the given text to the display.
 global brailler
 if not config.main['braille']['brailleSpoken']:
  return
 if not brailler:
  setup()
 brailler.braille(text, *args, **kwargs)

def CopyPostToClipboard (buffer=None, index=None):
 if not buffer:
  buffer = sessions.current_session.current_buffer
 if not index and index != 0:
  index = buffer.index
 formatted = buffer.format_item_clipboard(index)
 return Copy(formatted)

def Copy(text):
 #Copies text to the clipboard.
 if sys.platform == "win32":
  import win32clipboard
  win32clipboard.OpenClipboard()
  win32clipboard.EmptyClipboard()
  win32clipboard.SetClipboardText(text)
  win32clipboard.CloseClipboard()
 elif sys.platform == "linux2":
  import gtk
  cb = gtk.Clipboard()
  cb.set_text(text)
  cb.store()
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
   speaker = speech.Speaker(speech.outputs.Sapi5())
  else:
   speaker = speech.Speaker()
  brailler = braille.Brailler()
 except:
  return logging.exception("Output: Error during initialization.")
 try:
  if config.main['speech']['screenreader'] == 'SAPI':
   speaker.rate = config.main['speech']['rate']
   speaker.volume = config.main['speech']['volume']
   speaker.voice = config.main['speech']['voice']
 except:
  logging.exception("Unable to set sapi speech properties from configuration")
