import sessions
import wx

from twitter_message import TwitterMessageDialog

class NewTweetDialog (TwitterMessageDialog):
 def __init__(self, title=None, text="", *args, **kwargs):
  if title is None:
   title = _("Tweet")
  super(NewTweetDialog, self).__init__(*args, title=title, **kwargs)
  self.setup_message_field(text)
  #For viewing tweets, option to rt
  self.retweet = self.labeled_control(_("Retweet:"), wx.CheckBox)
  #Hide this by default
  self.retweet.Show(False)
  self.finish_setup()
  self.update_url_buttons()
