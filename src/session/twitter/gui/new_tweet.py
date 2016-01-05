# -*- coding: utf-8

import sessions
import wx
import io

from twitter_message import TwitterMessageDialog


class NewTweetDialog (TwitterMessageDialog):
 def __init__(self, title=None, text=u"", *args, **kwargs):
  if title is None:
   title = _("Tweet")
  super(NewTweetDialog, self).__init__(*args, title=title, **kwargs)
  self.setup_message_field(text)
  #For viewing tweets, options to rt and quote
  self.retweet = self.labeled_control(_("Retweet"), wx.CheckBox)
  self.quote = self.labeled_control(_("Quote"), wx.CheckBox)
  #Hide these by default
  self.retweet.Show(False)
  self.quote.Show(False)
  self.finish_setup()
  self.update_url_buttons()
