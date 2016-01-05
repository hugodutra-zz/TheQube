# -*- coding: utf-8 -*-

import sessions
import wx

from new_message import NewMessageDialog

class SelectableMessageDialog (NewMessageDialog):

 def __init__(self, selection=[u""], default=u"", text=u"", *args, **kwargs):
  self.recipients = selection
  self.default_recipient = default
  super(SelectableMessageDialog, self).__init__(*args, **kwargs)
  self.setup_recipient_field()
  self.setup_message_field(text)
  self.finish_setup(set_focus=False)

 def setup_recipient_field (self):
  self.selection = self.labeled_control(_("Recipient:"), wx.ComboBox, value=self.default_recipient, choices=self.recipients, style=wx.CB_DROPDOWN)
  self.selection.SetEditable(True)
  self.selection.Bind(wx.EVT_TEXT, self.selection_updated)
  self.selection.SetSizerProps(expand=True)

 def selection_updated (self, evt):
  evt.Skip()
  self.update_title()

 def update_title (self):
  length = self.getMessageLength()
  title = _("%s to %s") % (self.base_title, self.selection.GetValue())
  self.SetTitle(_("%s - %d of %d Characters") % (title, length, self.max_length))

 def finish_setup (self, *args, **kwargs):
  super(SelectableMessageDialog, self).finish_setup(*args, **kwargs)
  if not self.selection.GetValue():
   self.selection.SetFocus()
  else:
   self.message.SetFocus()
  if len(self.message.GetValue()) == 0:
   self.shorten.Disable()
   self.unshorten.Disable()
  else:
   self.shorten.Enable()
   self.unshorten.Enable()
  self.message.SetSelection(len(self.message.GetValue()),len(self.message.GetValue()))
