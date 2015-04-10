from logger import logger
logging = logger.getChild('core.gui.photos')

import os
import output
import sessions
import tempfile
import wx
from utils.thread_utils import call_threaded


from qube import SquareDialog

class AddPhotosDialog(SquareDialog):

 def __init__(self, title=None, *args, **kwargs):
  title = title or _("Attach audio")
  self.base_title = title
  super(RecordingDialog, self).__init__(title=title, *args, **kwargs)
  self.file = None
  self.recorded = False
  self.recording = None
  self.playing = None
  self.record = self.labeled_control(control=wx.Button, label=_("&Record"))
  self.record.Bind(wx.EVT_BUTTON, self.on_record)
  self.attach_existing = self.labeled_control(control=wx.Button, label=_("Attach existing audio &file..."))
  self.attach_existing.Bind(wx.EVT_BUTTON, self.on_attach_existing)
  self.play = self.labeled_control(control=wx.Button, label=_("&Play"))
  self.play.Bind(wx.EVT_BUTTON, self.on_play)
  self.play.Disable()
  self.discard = self.labeled_control(control=wx.Button, label=_("&Discard"))
  self.discard.Bind(wx.EVT_BUTTON, self.on_discard)
  self.discard.Disable()
  self.finish_setup()

 def create_buttons(self):
  self.attach = wx.Button(parent=self.pane, id=wx.ID_OK, label=_("&Attach!"))
  self.attach.Disable()
  self.cancel = wx.Button(parent=self.pane, id=wx.ID_CANCEL)
  self.SetEscapeId(wx.ID_CANCEL)

 def on_record(self, evt):
  evt.Skip()
  try:
   if self.recording != None: #Don't look at me like that. It's necessary
    self.stop_recording()
   else:
    self.start_recording()
  except:
   logging.exception("Recording blew up.")

 def start_recording(self):
  self.attach_existing.Disable()
  self.file = tempfile.mktemp(suffix='.wav')
  self.recording = sessions.current_session.record_sound(self.file)
  self.recording.play()
  self.record.SetLabel(_("&Stop"))
  output.speak(_("Recording."), True)

 def stop_recording(self):
  self.recording.stop()
  self.recording.free()
  output.speak(_("Stopped."), True)
  self.recorded = True
  self.record.SetLabel(_("&Record"))
  self.file_attached()

 def on_attach_existing(self, evt):
  evt.Skip()
  filter = 'Audio Files (*.mp3, *.wav, *.ogg)|*.mp3;*.wav;*.ogg'
  open_dlg = wx.FileDialog(parent=self.pane.Parent, message=_("Select audio file"), wildcard=filter, style=wx.OPEN)
  if open_dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  self.file = open_dlg.GetPath()
  self.file_attached()

 def file_attached(self):
  self.record.Disable()
  self.play.Enable()
  self.discard.Enable()
  self.attach.Enable()
  self.play.SetFocus()

 def on_discard(self, evt):
  evt.Skip()
  if self.playing:
   self._stop()
  if self.recording != None:
   self.attach.Disable()
   self.play.Disable()
  self.file = None
  self.record.Enable()
  self.attach_existing.Enable()
  self.record.SetFocus()
  self.discard.Disable()
  self.recording = None
  output.speak(_("Discarded."), True)

 def on_play(self, evt):
  evt.Skip()
  if not self.playing:
   call_threaded(self._play)
  else:
   self._stop()

 def _play(self):
  output.speak(_("Playing."), True)
  self.playing = sessions.current_session.play(self.file, honor_mute=False)
  self.play.SetLabel(_("&Stop"))
  try:
   while self.playing.is_playing:
    pass
   self.play.SetLabel(_("&Play"))
   self.playing.free()
   self.playing = None
  except:
   pass

 def _stop(self):
  output.speak(_("Stopped."), True)
  self.playing.stop()
  self.playing.free()
  self.play.SetLabel(_("&Play"))
  self.playing = None

 def postprocess(self):
  if self.file.lower().endswith('.wav'):
   output.speak(_("Transcoding audio."), True)
   sessions.current_session.recode_audio(self.file)
   self.wav_file = self.file
   self.file = '%s.ogg' % self.file[:-4]

 def cleanup(self):
  if self.playing and self.playing.is_playing:
   self.playing.stop()
  if self.recording != None:
   if self.recording.is_playing:
    self.recording.stop()
   try:
    self.recording.free()
   except:
    pass
   os.remove(self.file)
   if hasattr(self, 'wav_file'):
    os.remove(self.wav_file)
    del(self.wav_file)
  if hasattr(self, 'wav_file') and os.path.exists(self.file):
   os.remove(self.file)

