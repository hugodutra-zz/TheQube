import sessions
import wx

from user_list import UserListDialog

class UserInfoDialog (UserListDialog):
 def __init__(self, *args, **kwargs):
  super(UserInfoDialog, self).__init__(title=_("User profile"), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, *args, **kwargs)
#First Row
  wx.StaticText(self.pane, -1, _("User profile for:"))
  self.setup_users()
  self.finish_setup()
