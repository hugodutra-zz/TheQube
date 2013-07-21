import wx

from user_list import UserListDialog
from api_count import APICountDialog

class FavoritesDialog (UserListDialog, APICountDialog):

 def __init__(self, *args, **kwargs):
  super(FavoritesDialog, self).__init__(title=_("Display favorites"), *args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Favorites for:"))
  self.setup_users()
  self.setup_api_count_choice()
  self.finish_setup()
