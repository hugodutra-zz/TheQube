import wx

from core.gui import SquareDialog

class UserListDialog (SquareDialog):
 """A base class which provides one of our core.gui.with a user list.  Create the dialog passing in a list of usernames, and when you wish to insert the list, call self.setup_users()"""

 def __init__ (self, users=[""], *args, **kwargs):
  self._users = users
  super(UserListDialog, self).__init__(*args, **kwargs)

 def setup_users (self):
  self.users = wx.ComboBox(self.pane, wx.ID_ANY, value=self._users[0], choices=self._users, style=wx.CB_DROPDOWN)
  self.users.SetEditable(True)
