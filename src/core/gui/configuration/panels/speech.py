import accessible_output.speech.outputs.sapi5voice as sapi5voice
import config

from core.gui.configuration import ConfigurationPanel
import wx

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
  try:
   wx.StaticText(self, -1, _("SAPI speech voice"))
   self.SAPIVoice = wx.ComboBox(self, -1, style=wx.CB_READONLY, choices=sapi5voice.list_voices())
   self.SAPIVoice.SetSizerProps(expand=True)
   self.Bind(wx.EVT_COMBOBOX, self.VoicePreview, self.SAPIVoice)
  except:
   pass
  self.EnableSpeechRecognition = wx.CheckBox(self, -1, _("Enable speech recognition?"))
  self.finish_setup()

 def VoicePreview (self, evt):
  try:
   selected = sapi5voice.available_voices()[self.SAPIVoice.GetValue()]
   current = sapi5voice.available_voices()[config.main['speech']['voice']]
   sapi5voice.sapi5.Voice = selected
   sapi5voice.sapi5.Speak(selected.GetDescription(), 3)
   #Revert back to the current voice setting after previewing
   sapi5voice.sapi5.Voice = current
  except:
   pass
