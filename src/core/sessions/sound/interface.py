import output
import sessions

from core.sessions.interface.interface import Interface

class SoundInterface (Interface):

 def ToggleSessionMute(self):
  """Toggles between the different mute settings."""

  self.session.toggle_session_mute()
  self.session.announce_session_mute()

 def ToggleGlobalMute(self):
  """Globally mutes all Qwitter sessions"""

  self.session.toggle_global_mute()
  self.session.announce_global_mute()

 def IncreaseVolume(self):
  """Increases application-wide volume by 10%"""

  self.session.volume += 10
  self.session.play('boundary.wav', honor_mute=False)
  output.speak(_("Louder."), True)

 def DecreaseVolume(self):
  """Decreases application-wide volume by 10%"""

  self.session.volume -= 10
  self.session.play('boundary.wav', honor_mute=False)
  output.speak(_("Quieter."), True)
