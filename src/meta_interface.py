# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('meta_interface')

import application
import config
import core.gui
import global_vars
import output
import sessions
import threading
import shutdown
import wx
import signals
import i18n
from pydispatch import dispatcher
from utils.thread_utils import call_threaded
from utils.wx_utils import always_call_after, modal_dialog, question_dialog

class MetaInterface (object):

 def NextSession(self):
  """Moves to the next session in the list of active sessions."""

  sessions.SetSession(sessions.GetSessionIndex()+1)
  output.AnnounceSession()
  if hasattr(sessions.current_session, 'announce_session_mute'):
   sessions.current_session.announce_session_mute(True)

 def PrevSession(self):
  """Moves to the previous session in the list of active sessions."""

  sessions.SetSession(sessions.GetSessionIndex()-1)
  output.AnnounceSession()
  if hasattr(sessions.current_session, 'announce_session_mute'):
   sessions.current_session.announce_session_mute(True)

 def MainConfigDialog(self):
  """Shows a dialog in which you can configure global application settings."""
  new = modal_dialog(core.gui.configuration.MainConfigDialog, parent=application.main_frame, id=wx.ID_ANY, title=_("%s Configuration") % application.name)
  new.SetNewConfigValues()
  output.speak(_("Configuration saved."), 1)

 def Exit(self):
  """Exits The Qube."""
  if not hasattr(global_vars, 'shutdown_lock'):
   global_vars.shutdown_lock = threading.Lock()
  with global_vars.shutdown_lock:
   if config.main['client']['AskForExit']:
    d = question_dialog(parent=application.main_frame, caption=_("Exit %s") % application.name, message=_("Are you sure you wish to exit %s?") % application.name, style=wx.YES|wx.NO|wx.ICON_WARNING)
    if d!= wx.ID_YES:
     return output.speak(_("Canceled."), True)
   output.speak(_("Exiting %s.") % application.name, True)
   shutdown.exit()

 def StopSpeech(self):
  """Silences speech output."""
  output.speak("", 3) #using this hack to force silencing of SAPI5 speech

 def ToggleSpeechRecognition(self):
  """Toggles The Qube's ability to recognize spoken commands."""

  if config.main['recognition']['enabled']:
   logging.debug("Turning off speech recognition.")
   sessions.current_session.disable_speech_recognition()
   output.speak(_("Speech recognition off."), 1)
  else:
   logging.debug("Turning on speech recognition.")
   sessions.current_session.enable_speech_recognition()
   output.speak(_("Speech recognition on."), 1)

 def About(self):
  """Provides information about the currently active version of The Qube."""

  info = wx.AboutDialogInfo()
  info.Name = application.name
  info.Version = str(application.version)
  info.Copyright = _(u"Copyright © 2013 — 2014 %s." % application.author)
  info.WebSite = application.url
  application.main_frame.Raise()
  wx.AboutBox(info) 
  application.main_frame.Show(False)

 def ShowConfigurationDialog(self):
  """Displays the configuration dialog for the current session."""

  sessions.current_session.show_configuration_dialog()

 def DismissSession (self, session=None):
  """Removes the current session from the list of sessions."""
  if not session:
   session = sessions.current_session
  if sessions.sessions and len(sessions.sessions) > 1:
   sessions.RemoveSession(session)
  else:
   output.speak(_("Error: this is the only session."), True)

 def DeleteSession(self, session=None):
  """Completely deletes the given session and all of its associated data."""
  if not session:
   session = sessions.current_session
  if len (sessions.sessions) <= 1:
   return output.speak(_("Error: this is the only session."), True)
  d = wx.MessageDialog(None, _("Permanently delete all data associated with session %s?" % session.name), _("Delete Session"), wx.YES|wx.NO|wx.ICON_WARNING)
  d.Raise()
  choice = d.ShowModal()
  if choice == wx.ID_YES:
   sessions.RemoveSession(session, delete=True)
  else:
   return output.speak(_("Canceled."), True)

 def CurrentSession(self):
  """Announces the currently active session."""
  output.AnnounceSession()

 def NewSession(self):
  """Allows you to create a new session."""
  dlg = modal_dialog(core.gui.SessionManager.NewSessionDialog, parent=application.main_frame)
  kind = dlg.sessions.GetStringSelection()
  name = dlg.name.GetValue()
  if not name:
   output.speak(_("Please enter a name for this session."))
   return self.NewSession()
  try:
   new = sessions.SpawnSession(kind=kind, name=name)
  except:
   output.speak(_("Unable to spawn new %s session.") % kind, True)
   application.main_frame.Show(False)
   return
  sessions.SetSession(new)
  output.AnnounceSession()
  application.main_frame.Show(False)

 def ForceSyncToDisk(self):
  """Saves the current session's database to disk."""
  #FIXME Should be moved to storage session
  output.speak(_("Syncing storage to disk for %s session." % sessions.current_session.name), True)
  call_threaded(sessions.current_session.sync, forced=True, speak=True)

 @always_call_after
 def RenameSession(self):
  """Renames the active session."""
  dlg = wx.TextEntryDialog(parent=None, caption=_("Rename %s session") % sessions.current_session.name, message=_("Please enter a new name for session %s:") % sessions.current_session.name)
  dlg.Raise()
  if dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  name = dlg.GetValue()
  output.speak(_("Renaming session %s to %s, please wait.") %  (sessions.current_session.name, name), True)
  try:
   sessions.rename_session(sessions.current_session, name)
  except sessions.RenameError as e:
   return output.speak(_("There was an error renaming %s to %s: %s") % (sessions.current_session, name, e.args[0]))
  output.speak(_("Renaming session complete."))
  output.AnnounceSession(interrupt=False)

interface = MetaInterface
