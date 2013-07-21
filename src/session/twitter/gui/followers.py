import wx

from user_list import UserListDialog
from api_count import APICountDialog

class FollowersDialog (UserListDialog, APICountDialog):

 def __init__(self, *args, **kwargs):
  super(FollowersDialog, self).__init__(title=_("List Followers"), style=wx.DEFAULT_DIALOG_STYLE |wx.RESIZE_BORDER, *args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Followers for:"))
  self.setup_users()
  self.setup_api_count_choice()
  self.finish_setup()
