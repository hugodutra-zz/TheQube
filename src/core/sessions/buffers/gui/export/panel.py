from core.gui.configuration import ConfigurationPanel
import wx
import wx.lib.sized_controls as sc

#Main export panel object
class ExportPanel (ConfigurationPanel):
 def __init__(self, parent_nb, pageName, *args, **kwargs):
  #parent_nb must be in the argument list to prevent duplicate argument error.
  self.pageName = pageName
  super(ExportPanel, self).__init__(parent_nb, *args, **kwargs)
  self.dlg = self.parent_nb.GetParent()
  self.dlg.panels.append(self)

 def GetExportArgs(self):
  return {}

 def FindPage(self):
  for i in range(self.parent_nb.GetPageCount()):
   if self.parent_nb.GetPage(i) is self:
    return i
  return None

 def ShowPage(self, show = True):
  pageIndex = self.FindPage()
  if show and pageIndex is None:
   self.parent_nb.AddPage(self, self.pageName)
  elif not show and pageIndex is not None:
   self.parent_nb.RemovePage(pageIndex)
   