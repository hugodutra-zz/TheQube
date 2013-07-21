import wx

from user_list import UserListDialog
from api_count import APICountDialog

class IndividualDialog (UserListDialog, APICountDialog):

 def __init__(self, *args, **kwargs):
  super(IndividualDialog, self).__init__(title=_("Individual Timeline"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  #First Row
  wx.StaticText(self.pane, label=_("Buffer for:"))
  self.setup_users()
  self.setup_api_count_choice()
  self.finish_setup()

