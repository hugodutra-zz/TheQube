import sessions

from core.gui import NewMessageDialog

class TwitterMessageDialog (NewMessageDialog):

 def __init__ (self, max_length=None, *args, **kwargs):
  max_length = max_length or sessions.current_session.config['lengths']['tweetLength']
  super(TwitterMessageDialog, self).__init__(max_length=max_length, *args, **kwargs)
