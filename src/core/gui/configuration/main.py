from logger import logger
logging = logger.getChild("core.gui.configuration")

import application
import config
import global_vars
import i18n
import output

import sys
import wx

from core.gui.configuration import ConfigurationDialog

from core.gui.configuration.panels import *

from platform_utils.autostart import windows

class MainConfigDialog (ConfigurationDialog):
 def __init__(self, *args, **kwargs):
  super(MainConfigDialog, self).__init__(*args, **kwargs)
  self.languages = LanguagePanel(self.nb)
  self.nb.AddPage(self.languages, _("Language"))
  self.speech = SpeechPanel(self.nb)
  self.nb.AddPage(self.speech, _("Speech and Braille"))
  self.navigation = NavigationPanel(self.nb)
  self.nb.AddPage(self.navigation, _("Navigation"))
  self.misc = MiscPanel(self.nb)
  self.nb.AddPage(self.misc, _("Miscellaneous"))
  self.finish_setup(focus = self.languages.language)
  self.SetDefaultValues()

 def SetDefaultValues (self):
  self.speech.screenReader.SetValue(config.main['speech']['screenreader'])
  self.speech.SAPIRate.SetValue(config.main['speech']['rate'])
  self.speech.SAPIVolume.SetValue(config.main['speech']['volume'])
  try:
   self.speech.SAPIVoice.SetValue(config.main['speech']['voice'])
  except Exception as svexc:
   logging.exception("Error setting default sapi voice: {}".format(svexc))
  self.speech.braille.SetValue(config.main['braille']['brailleSpoken'])
  self.speech.EnableSpeechRecognition.SetValue(config.main['recognition']['enabled'])
  self.navigation.step.SetValue(config.main['client']['step'])
  self.navigation.timeStepHours.SetValue(config.main['client']['timeStep'] / 60)
  self.navigation.timeStepMins.SetValue(config.main['client']['timeStep'] % 60)
  self.navigation.undoStackSize.SetValue(config.main['client']['undoStackSize'])
  self.misc.AutoStart.SetValue(config.main['client']['AutoStart'])
  self.misc.AskForExit.SetValue(config.main['client']['AskForExit'])
  self.misc.shorteners.SetValue(config.main['shortener']['urlShortener'])
  self.misc.audioServices.SetValue(config.main['AudioServices']['service'])
  self.misc.sndupKey.SetValue(config.main['AudioServices']['sndUpAPIKey'])
  self.misc.sendMessagesWithEnterKey.SetValue(config.main['UI']['sendMessagesWithEnterKey'])
  self.misc.stdKeyHandling.SetValue(config.main['UI']['stdKeyHandling'])

 def SetNewConfigValues (self):
  config.main['languages']['current'] = i18n.lang_from_printable_language(self.languages.language.GetValue())
  config.main['speech']['screenreader'] = self.speech.screenReader.GetValue()
  logging.info("Screen reader set to: %s" % config.main['speech']['screenreader'])
  config.main['speech']['rate'] = self.speech.SAPIRate.GetValue()
  logging.info("SAPI speech rate set to: %d" % config.main['speech']['rate'])
  config.main['speech']['volume'] = self.speech.SAPIVolume.GetValue()
  logging.info("SAPI volume set to: %d "% config.main['speech']['volume'])
  try:
   config.main['speech']['voice'] = self.speech.SAPIVoice.GetValue()
   logging.info("SAPI voice set to: %s." % config.main['speech']['voice'])
  except:
   logging.exception("Error setting new SAPI voice config value.")
  config.main['recognition']['enabled'] = self.speech.EnableSpeechRecognition.GetValue()
  config.main['client']['step'] = int(self.navigation.step.GetValue()) or 5
  config.main['client']['timeStep'] = int(self.navigation.timeStepHours.GetValue()*60 + self.navigation.timeStepMins.GetValue()) or 60
  config.main['client']['undoStackSize']=int(self.navigation.undoStackSize.GetValue()) or 100
  config.main['braille']['brailleSpoken'] = self.speech.braille.GetValue()
  config.main['client']['AutoStart'] = self.misc.AutoStart.GetValue()
  logging.info("AutoStart set to: %d." % config.main['client']['AutoStart'])
  config.main['client']['AskForExit'] = self.misc.AskForExit.GetValue()
  logging.info("AskForExit set to: %d." % config.main['client']['AskForExit'])
  config.main['shortener']['urlShortener'] = self.misc.shorteners.GetValue()
  logging.info("urlShortener set to: %s" % config.main['shortener']['urlShortener'])
  config.main['AudioServices']['service'] = self.misc.audioServices.GetValue()  
  logging.info("Audio service set to: %s." % config.main['AudioServices']['service'])  
  config.main['AudioServices']['sndUpAPIKey'] = self.misc.sndupKey.GetValue()
  logging.info("SndUp API key set to: %s." % config.main['AudioServices']['sndUpAPIKey'])
  config.main['UI']['stdKeyHandling'] = self.misc.stdKeyHandling.GetValue()
  logging.info("stdKeyHandling set to: %d" % config.main['UI']['stdKeyHandling'])
  config.main['UI']['sendMessagesWithEnterKey'] = self.misc.sendMessagesWithEnterKey.GetValue()
  logging.info("sendMessagesWithEnterKey set to: %d" % config.main['UI']['sendMessagesWithEnterKey'])
  config.main.write()
  i18n.setup()
  output.setup()
  if hasattr(sys, 'frozen') and not global_vars.portable:
   windows.setAutoStart(application.name, config.main['client']['AutoStart'])
