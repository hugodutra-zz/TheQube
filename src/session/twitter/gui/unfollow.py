import wx

from user_list import UserListDialog

class UnfollowDialog (UserListDialog):

 def __init__(self, *args, **kwargs):
  super(UnfollowDialog, self).__init__(title=_("Unfollow someone"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  #First Row
  wx.StaticText(parent=self.pane, label=_("Unfollow who:"))
  self.setup_users()
  #Radio buttons
  self.action = wx.RadioBox(parent=self.pane, label=_("Action:"), choices=[_('Unfollow'), _('Block'), _('Report as spam')])
  self.action.SetSizerProps(expand=True)
  self.finish_setup()
