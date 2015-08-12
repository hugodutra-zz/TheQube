from logger import logger
logging = logger.getChild('core.gui.photos')

import os
import output
import sessions
import tempfile
import wx
from utils.thread_utils import call_threaded


from qube import SquareDialog

class AddPhotoDialog(SquareDialog):

 def __init__(self, title=None, *args, **kwargs):
  title = title or _("Add photo")
  self.base_title = title
  super(AddPhotoDialog, self).__init__(title=title, *args, **kwargs)
  self.file = None
  filter = _('Image Files (*.jpg, *.png, *.gif)|*.jpg;*.png;*.gif')
  open_dlg = wx.FileDialog(parent=self.pane.Parent, message=_("Select audio file"), wildcard=filter, style=wx.OPEN)
  if open_dlg.ShowModal() != wx.ID_OK:
   return output.speak(_("Canceled."), True)
  self.file = open_dlg.GetPath()
  self.file_attached()
  self.finish_setup()

 def create_buttons(self):
  self.add = wx.Button(parent=self.pane, id=wx.ID_OK, label=_("&Add!"))
  self.add.Disable()
  self.cancel = wx.Button(parent=self.pane, id=wx.ID_CANCEL)
  self.SetEscapeId(wx.ID_CANCEL)

 def file_attached(self):
  self.add.Enable()
  self.add.SetFocus()

 def cleanup(self):
  os.remove(self.file)
