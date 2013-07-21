from logger import logger
logging = logger.getChild('core.buffers.audio')

import audio_services
import output
from utils.thread_utils import call_threaded

from core.sessions.buffers import field_metadata as meta
from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.buffers.buffers.messages import Messages

class Audio(Messages):

 def __init__(self, *args, **kwargs):
  super(Audio, self).__init__(*args, **kwargs)
  self.set_field('audio', _("Attached Audio"), (lambda item: bool(self.find_audio_handler(item=item))), field_type=meta.FT_BOOL)
 
 @buffer_defaults
 def interact (self, index=None):
  if self.find_audio_handler(index):
   call_threaded(self.interact_with_audio, index)
  else:
   super(Audio, self).interact(index=index)

 @buffer_defaults
 def find_audio_handler (self, index=None, item=None):
  urls = self.get_urls(item=item)
  for url in urls:
   try:
    transformer = audio_services.find_url_transformer(url)
    if transformer:
     return transformer(url)
   except:
    pass

 @buffer_defaults
 def interact_with_audio (self, index=None):
  url = self.find_audio_handler(index)
  if self._url_matches_playing_item(url) and self.session.currently_playing.is_playing:
   return self._stop()
  output.speak(_("playing audio."), True)
  self.session.user_playback(url, stream=True)

 def _url_matches_playing_item(self, url):
  return self.session.currently_playing is not None and url == self.session.currently_playing.url

 @buffer_defaults
 def remove_item(self, index=None):
  url = self.find_audio_handler(index)
  if self._url_matches_playing_item(url):
   self._stop()
  super(Audio, self).remove_item(index=index)

 def _stop(self):
  self.session.stop_user_playback()
  output.speak(_("audio playback stopped."), True)
