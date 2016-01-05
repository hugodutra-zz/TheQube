# -*- coding: utf-8 -*-

import wx
import sessions

from core.gui import SelectableMessageDialog
from twitter_message import TwitterMessageDialog

class NewDirectDialog (TwitterMessageDialog, SelectableMessageDialog):
 def __init__ (self, max_length=None, *args, **kwargs):
  max_length = max_length or sessions.current_session.config['lengths']['dmLength']
  super(TwitterMessageDialog, self).__init__(max_length=max_length, *args, **kwargs)
