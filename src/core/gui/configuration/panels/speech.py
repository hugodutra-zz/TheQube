from accessible_output2.outputs.sapi5 import SAPI5
import config

from core.gui.configuration import ConfigurationPanel
import wx
from logger import logger
logging = logger.getChild('config.panels.speech')

class SpeechPanel (ConfigurationPanel):
 def __init__ (self, *args, **kwargs):
  super(SpeechPanel, self).__init__(*args, **kwargs)
  wx.StaticText(self, -1, _("Speech output"))
  self._first = self.screenReader = wx.ComboBox(self, -1, value = "auto", choices=['auto', 'SAPI'], style=wx.CB_READONLY)
  self.screenReader.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("SAPI speech rate"))
  self.SAPIRate = wx.SpinCtrl(self, -1)
  self.SAPIRate.SetRange(1,10)
  self.SAPIRate.SetValue(4)
  self.SAPIRate.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("SAPI speech volume"))
  self.SAPIVolume = wx.SpinCtrl(self, -1)
  self.SAPIVolume.SetRange(1,100)
  self.SAPIVolume.SetValue(100)
  self.SAPIVolume.SetSizerProps(expand=True)
  wx.StaticText(self, -1, _("SAPI speech voice"))
  self.SAPIVoice = wx.ComboBox(self, -1, style=wx.CB_READONLY, choices=SAPI5().list_voices())
  self.SAPIVoice.SetSizerProps(expand=True)
  self.Bind(wx.EVT_COMBOBOX, self.VoicePreview, self.SAPIVoice)
  wx.StaticText(self, wx.ID_ANY, _("Braille Output:"))
  self.braille = wx.CheckBox(self, wx.ID_ANY, _("Braille spoken text"))
  self.EnableSpeechRecognition = wx.CheckBox(self, -1, _("Enable speech recognition"))
  self.finish_setup()

 def VoicePreview (self, evt):
  try:
   selected = Sapi5().available_voices()[self.SAPIVoice.GetValue()]
   current = Sapi5().available_voices()[config.main['speech']['voice']]
   Sapi5().Sapi5().Voice = selected
   Sapi5().Sapi5().Speak(selected.GetDescription(), 3)
   #Revert back to the current voice setting after previewing
   Sapi5().Sapi5().Voice = current
  except Exception as e:
   logging.exception("Unable to try voice: {0}".format(e))
