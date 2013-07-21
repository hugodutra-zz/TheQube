import config
import sessions
import wx

from core.gui import SquareDialog

class UpdateProfileDialog(SquareDialog):

 def __init__(self, user, *args, **kwargs):
  super(UpdateProfileDialog, self).__init__(title=_("Update profile"), *args, **kwargs)
  self.name = self.labeled_control(_("Name (Maximum of %d characters).") % sessions.current_session.config['lengths']['nameLength'], wx.TextCtrl, style=wx.TE_MULTILINE | wx.WANTS_CHARS)
  value=user['name']
  if value is not None and value != "None":
   self.name.SetValue(value)
  self.name.Bind(wx.EVT_CHAR, self.charPressed)
  self.name.SetSizerProps(expand=True)
  self.url = self.labeled_control(_("URL (Maximum of %d characters).") % sessions.current_session.config['lengths']['URLLength'], wx.TextCtrl, style=wx.TE_MULTILINE | wx.WANTS_CHARS)
  value=unicode(user['url'])
  if value is not None and value != "None":
   self.url.SetValue(value)
  self.url.Bind(wx.EVT_CHAR, self.charPressed)
  self.url.SetSizerProps(expand=True)
  self.location = self.labeled_control(_("Location (Maximum of %d characters).") % sessions.current_session.config['lengths']['locationLength'], wx.TextCtrl, style=wx.TE_MULTILINE | wx.WANTS_CHARS)
  value=unicode(user['location'])
  if value is not None and value != "None":
   self.location.SetValue(value)
  self.location.Bind(wx.EVT_CHAR, self.charPressed)
  self.location.SetSizerProps(expand=True)
  size = self.Size
  size[0] = size[0] / 2
  size[1] = -1
  self.description = self.labeled_control(_("Bio (Maximum of %d characters).") % sessions.current_session.config['lengths']['descriptionLength'], wx.TextCtrl, style=wx.TE_MULTILINE|wx.WANTS_CHARS, size=size)
  value=unicode(user['description'])
  if value is not None and value != "None":
   self.description.SetValue(value)
  self.description.Bind(wx.EVT_TEXT, self.textUpdated)
  self.description.Bind(wx.EVT_CHAR, self.charPressed)
  self.description.SetSizerProps(expand=True)
  self.finish_setup()

 def textUpdated(self, evt):
  evt.Skip()
  self.Fit()

 def charPressed(self, evt):
  object = evt.GetEventObject()
  key = evt.GetKeyCode()
  modifiers = evt.GetModifiers()
  if config.main['UI']['stdKeyHandling'] and key in (wx.WXK_END, wx.WXK_HOME):
   evt.Skip()
  elif key == wx.WXK_HOME and not modifiers:
   object.SetInsertionPoint(0)
  elif key == wx.WXK_END and not modifiers:
   object.SetInsertionPointEnd()
  elif key == wx.WXK_HOME and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), 0)
  elif key == wx.WXK_END and modifiers == wx.MOD_SHIFT:
   object.SetSelection(object.GetInsertionPoint(), len(object.GetValue()))
  elif key == 1 and modifiers == wx.MOD_CONTROL:
   object.SetInsertionPoint(0)
   object.SetSelection(0, len(object.GetValue()))
  elif key == 13:
   self.EndModal(wx.ID_OK)
  else:
   evt.Skip()
