from logger import logger
logging = logger.getChild("sessions.twitter.gui.configuration")

import os
import paths
import wx

from core.gui.configuration import ConfigurationDialog
from panels import *

class TwitterConfigDialog (ConfigurationDialog):

 def __init__(self, session, *args, **kwargs):
  self.session = session
  if not kwargs.has_key('title'):
   kwargs['title'] = _("Twitter Configuration")
  if kwargs.has_key('config'):
   self.__dict__['config'] = kwargs['config']
   del(kwargs['config'])
  if not kwargs.has_key('pos'):
   kwargs['pos'] = (0,0)
  super(TwitterConfigDialog, self).__init__(*args, **kwargs)
  self.sounds = SoundPanel(self.nb)
  self.nb.AddPage(self.sounds, _("Sounds"))
  self.templates = TemplatesPanel(self.session, self.nb)
  self.nb.AddPage(self.templates, _("Templates"))
  self.misc = MiscPanel(self.nb)
  self.nb.AddPage(self.misc, _("Miscellaneous"))
  self.finish_setup(focus = self.sounds.SoundPack)

 def SetDefaultValues (self):
  self.sounds.mute.SetValue(self.config['sounds']['mute'])
  soundpacks = os.listdir(paths.sounds_path())
  self.sounds.SoundPack.SetItems(soundpacks)
  self.sounds.SoundPack.SetValue(self.config['sounds']['soundPack'])
  self.templates.default_followers_friends.SetValue(self.config['templates']['default_followers_friends'])
  self.templates.default_template.SetValue(self.config['templates']['default_template'])
  self.templates.reply.SetValue(self.config['templates']['reply'])
  self.templates.retweet.SetValue(self.config['templates']['retweet'])
  self.templates.search.SetValue(self.config['templates']['search'])
  self.templates.user_info.SetValue(self.config['templates']['user_info'])
  self.misc.DMSafeMode.SetValue(self.config['UI']['DMSafeMode'])
  self.misc.confirmRemovePost.SetValue(self.config['UI']['confirmRemovePost'])
  self.misc.RTStyle.SetItems([_("Ask whether comments are to be added (recommended)"), _("Never add comments (automatically retweet)"), _("Always add comments (old style)")])
  self.misc.RTStyle.SetValue(self.misc.RTStyle.GetItems()[self.config['UI']['RTStyle']])
  self.misc.replyToSelf.SetValue( self.config['UI']['replyToSelf'])
  self.misc.WorkOffline.SetValue(self.config['security']['workOffline'])
  self.misc.Fit()
  self.sizer.Fit(self)
  self.SetSizer(self.sizer)
#  self.Fit()

 def SetNewConfigValues (self):
  logging.debug("Saving configuration from dialog.")
  self.config['sounds']['soundPack'] = self.sounds.SoundPack.GetValue()
  logging.info("Sound pack set to: %s" % self.config['sounds']['soundPack'])
  self.config['sounds']['mute'] = self.sounds.mute.GetValue()
  logging.info("Mute status set to: %s" % self.config['sounds']['mute'])
  self.config['templates']['default_followers_friends'] = self.templates.default_followers_friends.GetValue()
  self.config['templates']['default_template'] = self.templates.default_template.GetValue()
  self.config['templates']['reply'] = self.templates.reply.GetValue()
  self.config['templates']['retweet'] = self.templates.retweet.GetValue()
  self.config['templates']['search'] = self.templates.search.GetValue()
  self.config['templates']['user_info'] = self.templates.user_info.GetValue()
  self.config['UI']['DMSafeMode'] = self.misc.DMSafeMode.GetValue()
  logging.info("DMSafeMode set to: %d" % self.config['UI']['DMSafeMode'])
  self.config['UI']['confirmRemovePost'] = self.misc.confirmRemovePost.GetValue()
  logging.info("confirmRemovePost set to: %d" % self.config['UI']['confirmRemovePost'])
  self.config['UI']['RTStyle'] = self.misc.RTStyle.GetItems().index(self.misc.RTStyle.GetValue())
  logging.info("RTStyle set to: %d" % self.config['UI']['RTStyle'])
  self.config['UI']['replyToSelf'] = self.misc.replyToSelf.GetValue()
  logging.info("ReplyToSelf set to: %s." % self.config['UI']['replyToSelf'])
  self.config['security']['workOffline'] = self.misc.WorkOffline.GetValue()
  logging.info("Work offline set to: %s" % self.config['security']['workOffline'])
