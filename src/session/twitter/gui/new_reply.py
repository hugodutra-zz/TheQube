# -*- coding: utf-8 -*-

import sessions
import wx

from core.gui import SelectableMessageDialog
from twitter_message import TwitterMessageDialog

class NewReplyDialog (TwitterMessageDialog, SelectableMessageDialog):

 def setup_recipient_field(self, *args, **kwargs):
  super(NewReplyDialog, self).setup_recipient_field(*args, **kwargs)
  self.mention_all = wx.Button(parent=self.pane, label=_("&Mention all users"))
  self.mention_all.Bind(wx.EVT_BUTTON, self.mention_all_pressed)
  if len(self.recipients) == 1:
   self.mention_all.Disable()

 def mention_all_pressed(self, evt):
  evt.Skip()
  for user in self.recipients:
   if user != self.selection.GetValue() and self.message.GetValue().lower().find('@'+user.lower()) == -1 and not sessions.current_session.is_current_user(user):
    point = self.message.GetInsertionPoint()
    self.message.SetValue('@'+user+' '+self.message.GetValue())
    self.message.SetInsertionPoint(point + len(user) + 2)
  self.message.SetFocus()

 def getMessageLength(self):
  return len(self.message.GetValue())+len("@%s " % self.selection.GetValue())
