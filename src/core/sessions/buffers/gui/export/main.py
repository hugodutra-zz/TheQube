import wx

from core.gui.configuration import ConfigurationDialog
import wx
import sessions

from panels import *

class MainExportDialog(ConfigurationDialog):
 def __init__(self, *args, **kwargs):
  if not kwargs.has_key('title'):
   kwargs['title'] = _("Export")
  super(MainExportDialog, self).__init__(*args, **kwargs)
  self.session = sessions.current_session
  #Panels automatically append themselves to this list.
  self.panels = []
  #This is for a simple change handler.
  self.handlers = {}
  self.format = FormatPanel(self.nb)
  self.items = ItemsPanel(self.nb)
  for panel in self.panels:
   panel.ShowPage()
   panel.Fit()
  self.finish_setup(focus = self.format._first)
  if self.format.exportFormat.GetCount() > 0:
   self.format.SetFormatIndex(0)

 def GetExporter(self):
  exporterClass = self.format.GetExporterClass()
  if exporterClass is None:
   return None
  args = {}
  for panel in self.panels:
   args.update(panel.GetExportArgs())
  return exporterClass(**args)

 def IsExportAvailable(self):
  return self.format.exportFormat.GetCount() > 0 and self.items.buffer.GetCount() > 0

 def AddHandler(self, name, handler):
  if name not in self.handlers:
   self.handlers[name] = []
  self.handlers[name].append(handler)
 
 def RemoveHandler(self, name, handler):
  index = self.handlers[name].index(handler)
  del self.handlers[name][index]
  if len(self.handlers[name]) == 0:
   del self.handlers[name]

 def CallHandlers(self, name, value):
  if name in self.handlers:
   for handler in self.handlers[name]:
    handler(value)
   for panel in self.panels:
    panel.Layout()
   self.nb.Layout()
   self.Layout()

 def Destroy(self):
  self.handlers = {}
  for panel in self.panels:
   panel.ShowPage(False)
   panel.Destroy()
  super(MainExportDialog, self).Destroy()
