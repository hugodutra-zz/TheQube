import wx

from user_list import UserListDialog

class FollowDialog (UserListDialog):

 def __init__(self, *args, **kwargs):
  super(FollowDialog, self).__init__(title=_("Follow someone"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  wx.StaticText(parent=self.pane, label=_("Follow who:"))
  self.setup_users()
  self.updates =wx.CheckBox(parent=self.pane, label=_("Mobile Updates"))
  self.updates.SetSizerProps(expand=True)
  self.finish_setup()
