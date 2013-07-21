from core.sessions.buffers.buffer_defaults import buffer_defaults

import os
import output
import threading
from utils.thread_utils import call_threaded

from core.sessions.buffers import field_metadata as meta
from utils.thread_utils import call_threaded

from main import GoogleVoice

class Voicemail (GoogleVoice):
 _base_path = "voicemail"
 _states = dict(not_downloaded=0, downloading=1, downloaded=2, playing=3)

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  super(Voicemail, self).__init__(*args, **kwargs)
  self.item_name = _("voicemail")
  self.item_name_plural = _("voicemails")
  self.voicemail_sounds = dict()
  if not os.path.exists(self.voicemail_path):
   os.mkdir(self.voicemail_path)
  self.default_template = 'voicemail'
  self.set_field('state', _("Item state"), None, field_type=meta.FT_NUMERIC)
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  return self.session.gv.voicemail().folder['messages']

 def process_update(self, update, *args, **kwargs):
  update = super(Voicemail, self).process_update(update)
  for i in update:
   i['state'] = self._states['not_downloaded']
  return update

 def download_voicemail (self, index=None):
  output.speak(_("Downloading voicemail..."), True)
  with self.session.storage_lock:
   self[index]['state'] = self._states['downloading']
  res =  self.session.gv.download(self[index]['id'], self.voicemail_path)
  with self.session.storage_lock:
   self[index]['location'] = res
   self[index]['state'] = self._states['downloaded']

 @property
 def voicemail_path(self):
  return os.path.join(self.session.session_path, self._base_path)

 @buffer_defaults
 def do_interact (self, index=None):
  call_threaded(self.do_interact, index=index)

 @buffer_defaults
 def interact (self, index=None):
  state = self[index]['state']
  if state == self._states['downloaded']:
   self.play_voicemail(index=index)
  elif state == self._states['not_downloaded']:
   self.download_voicemail(index=index)
   if self.session.config['UI']['autoPlayVoicemail']:
    self.play_voicemail(index=index)
  elif state == self._states['playing']:
   self.stop_voicemail(index=index)
  else:
   self.play_voicemail(index=index)

 def play_voicemail (self, index=None):
  output.speak(_("Playing voicemail from %s") % self[index]['displayNumber'])
  vm_id = self[index]['id']
  self.voicemail_sounds[vm_id] = self.session.play(self[index]['location'])
  with self.session.storage_lock:
   self[index]['state'] = self._states['playing']

 def stop_voicemail (self, index=None):
  vm_id = self[index]['id']
  self.voicemail_sounds[vm_id].stop()
  del(self.voicemail_sounds[vm_id])
  with self.session.storage_lock:
   self[index]['state'] = self._states['downloaded']
  output.speak(_("Stopped."), True)

