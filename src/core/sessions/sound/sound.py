from logger import logger
logging = logger.getChild('sessions.sound.main')

from glob import glob
import config
import global_vars
import os
import output
import paths
import subprocess
import tempfile
from utils.repeating_timer import RepeatingTimer
from sound_lib.main import BassError
from sound_lib import recording, stream, input as sound_input, output as sound_output

from core.sessions.configuration.configuration import Configuration
from core.sessions.interface.main import Interface

class Sound (Configuration, Interface):

 MAX_OUTPUT_RESETS = 2 #How many times do we let the play method reset the output if sounds won't play to pickup soundcard changes?

 def __init__ (self, *args, **kwargs):
  super(Sound, self).__init__(*args, **kwargs)
  self.setup_sound()
  self.currently_playing = None
  self.sounds = []
  self.announce_session_mute(first=True)
  self.sound_cleaner = RepeatingTimer(30, self.cleanup_sounds)
  self.sound_cleaner.start()
  self.delete_old_tempfiles()

 @staticmethod
 def delete_old_tempfiles():
  for f in glob(os.path.join(tempfile.gettempdir(), 'tmp*.wav')):
   try:
    os.remove(f)
   except:
    pass

 def setup_sound(self, forced=False):
  if forced or not getattr(global_vars, 'sound_output', None):
   logging.debug("Initializing sound subsystem.")
   if hasattr(global_vars, 'sound_output') and global_vars.sound_output:
    global_vars.sound_output.free()
   try:
    global_vars.sound_output = sound_output.Output()
    global_vars.sound_input = sound_input.Input()
    global_vars.sound_output.volume = config.main['sounds']['volume']
   except:
    global_vars.sound_output = None
    global_vars.sound_input = None
  if hasattr(global_vars, 'sound_output') and 'sounds' in self.config and 'defaultSound' in self.config['sounds']:
   self.default_sound = self.config['sounds']['defaultSound']

 def play(self, file, this_retry=0, honor_mute=True):
  if honor_mute and (config.main['sounds']['mute'] or self.config['sounds']['mute']):
   return
  if not os.path.split(file)[0]: #it's just the file!
   try:
    file = self.find_sound_file(os.path.split(file)[1])
   except IOError: #The file wasn't found
    return
  try:
   snd = stream.FileStream(file=unicode(file), flags=stream.BASS_UNICODE)
   snd.play()
  except BassError as e:
   if this_retry < self.MAX_OUTPUT_RESETS:
    self.setup_sound(forced=True)
    return self.play(file, this_retry=this_retry+1)
   raise e
  self.sounds.append(snd)
  return snd

 def play_stream (self, url):
  try:
   snd = stream.URLStream(url=str(url.encode('utf-8')))
  except BassError as e:
   if e.code == 32:
    output.speak(_("No internet connection could be opened."), True)
   else:
    logging.exception("Unable to play stream")
    output.speak(_("Unable to play audio."), True)
   raise e
  snd.play()
  self.sounds.append(snd)
  return snd

 def record_sound(self, filename):
  try:
   val = recording.WaveRecording(filename=filename)
  except BassError as e:
   global_vars.sound_input = sound_input.Input()
   val = recording.WaveRecording(filename=filename)
  return val

 def find_sound_file (self, file):
  #Check if the session has a soundpack and if so play the sound from that
  if not 'soundPack' in self.config['sounds']:
   sound_file = paths.sounds_path('standard\\%s' % file)
  else:
   if not os.path.exists(paths.sounds_path(self.config['sounds']['soundPack'])):
    logging.warning("Unable to find soundpack %s" % self.config['sounds']['soundPack'])
    return
   sound_file = paths.sounds_path(r'%s\%s' % (self.config['sounds']['soundPack'], file))
  if not os.path.exists(sound_file):
   logging.warning('Unable to find sound file %r' % file)
   raise IOError, "Unable to find sound file"
  return sound_file

 def toggle_session_mute (self):
  self.config['sounds']['mute'] = not self.config['sounds']['mute']

 def announce_session_mute (self, first=False):
  if not self.config['sounds']['mute'] and not first:
   output.speak(_("Session mute off"), True)
  elif self.config['sounds']['mute']:
   output.speak(_("Session mute on"), not first)
  if first:
   self.announce_global_mute(first=first)

 def announce_global_mute (self, first=False):
  if not config.main['sounds']['mute'] and not first:
   output.speak(_("Global mute off"), True)
  elif config.main['sounds']['mute']:
   output.speak(_("Global mute on"), not first)

 def toggle_global_mute(self):
  config.main['sounds']['mute'] = not config.main['sounds']['mute']
  config.main.write()

 def cleanup_sounds(self):
  old_len = len(self.sounds)
  for i in self.sounds:
   if i.is_active():
    continue
   try:
    i.free()
   except:
    pass
   self.sounds.remove(i)
  if not self.sounds:
   self.setup_sound()

 def get_volume (self):
  return global_vars.sound_output.volume

 def set_volume (self, volume):
  if volume <= 0:
   volume = 0
  config.main['sounds']['volume'] = volume
  global_vars.sound_output.volume = volume
  config.main.write()

 volume = property(get_volume, set_volume)

 def shutdown(self, *args, **kwargs):
  try:
   self.sound_cleaner.stop()
   logging.debug("%s: Sound Cleaner: Deactivated timer." % self)
  except:
   logging.exception("%s: Sound Cleaner: Error shutting down timer." % self)
  for i in self.sounds:
   i.stop()
  self.cleanup_sounds()
  super(Sound, self).shutdown(*args, **kwargs)

 def recode_audio(self, filename, quality=4.5):
  subprocess.call(r'"%s" -q %r "%s"' % (paths.app_path('oggenc2.exe'), quality, filename))

 def user_playback(self, path, stream=False):
  if self.currently_playing is not None:
   self.stop_user_playback()
  if not stream:
   self.currently_playing = self.play(path, honor_mute=False)
  else:
   self.currently_playing = self.play_stream(path)

 def stop_user_playback(self):
  try:
   self.currently_playing.stop()
   self.currently_playing.free()
  except BassError:
   pass
  self.currently_playing = None

