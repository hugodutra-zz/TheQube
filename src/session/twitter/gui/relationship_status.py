import sessions
import wx

from user_list import UserListDialog

class RelationshipStatusDialog (UserListDialog):
 def __init__(self, *args, **kwargs):
  super(RelationshipStatusDialog, self).__init__(title=_("Relationship"), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, *args, **kwargs)
#First Row
  wx.StaticText(self.pane, -1, _("Relationship status between:"))
  self.setup_users()
#Second Row
  self.users2 = self.labeled_control(_("And:"), wx.ComboBox, value=self._users[-1], choices=self._users, style=wx.CB_DROPDOWN)
  self.users2.SetEditable(True)
  self.finish_setup()
