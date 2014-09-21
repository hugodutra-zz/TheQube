import wx

class FileDialog(wx.FileDialog):

 def __init__(self, filetypes=None, *args, **kwargs):
  wildcard = ""
  if filetypes is not None:
   for i in filetypes:
    ft = '%s|%s|' % (i[0], i[1])
    wildcard = '%s%s' % (wildcard, ft)
   wildcard = wildcard[:-1]
  super(FileDialog, self).__init__(wildcard=wildcard, *args, **kwargs)

class OpenDialog(FileDialog):

 def __init__(self, style=wx.ID_OPEN, *args, **kwargs):
  super(OpenDialog, self).__init__(style=style, *args, **kwargs)

class SaveDialog(FileDialog):

 def __init__(self, style=wx.ID_SAVE, *args, **kwargs):
  super(SaveDialog, self).__init__(style=style, *args, **kwargs)

