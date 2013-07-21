import wx
from core.sessions.buffers.gui.export import ExportPanel
from core.sessions.buffers import exporter
import os.path

class FormatPanel (ExportPanel):
 def __init__(self, *args, **kwargs):
  super(FormatPanel, self).__init__(pageName = _("Format"), *args, **kwargs)
  wx.StaticText(self, label=_("Export Format"))
  self._first = self.exportFormat = wx.ComboBox(self, style = wx.CB_READONLY)
  self.exportFormat.SetSizerProps(expand = True)
  self.exportFormat.Bind(wx.EVT_COMBOBOX, self.format_changed)
  self.filename_label = wx.StaticText(self, label = _("Filename"))
  self.filename = wx.TextCtrl(self, style = wx.TE_MULTILINE | wx.TE_READONLY)
  self.filename.SetSizerProps(expand = True)
  self.saveAs = wx.Button(self, label = _("Save As"))
  self.saveAs.Bind(wx.EVT_BUTTON, self.saveAs_click)
  self.exportMore = wx.CheckBox(self, label = _("Export more?"))
  self.exportMore.SetValue(False)
  self.finish_setup()
  formats = exporter.GetSupportedFormats()
  self.fileFilters = []
  wildcards = []
  for format in formats:
   self.exportFormat.Append(format.GetName(), format)
   self.fileFilters.append(format.GetFileExtension())
   wildcards.append(u"{name} (*.{ext})|*.{ext}".format(name = format.GetName(), ext = format.GetFileExtension()))
  self.saveAsDlg = wx.FileDialog(self, wildcard = u"|".join(wildcards), style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
  self.dlg.AddHandler('format', self.HandleFormatChange)

 def HandleFormatChange(self, format):
  supportedArgs = {}
  if format is not None:
   supportedArgs = format.GetSupportedArgs()
   filename = self.filename.GetValue()
   if len(filename) > 0:
    (basename, ext) = os.path.splitext(filename)
    if len(ext) > 0:
     filename = '{0}.{1}'.format(basename, format.GetFileExtension())
     self.filename.SetValue(filename)
  self.filename_label.Show('filename' in supportedArgs)
  self.filename.Show("filename" in supportedArgs)
  self.saveAs.Show("filename" in supportedArgs)
 
 def GetExportArgs(self):
  kwargs = {}
  if self.filename.IsShown():
   kwargs['filename'] = self.filename.GetValue()
  return kwargs
 
 def GetExporterClass(self, index = None):
  if index is None:
   index = self.exportFormat.GetSelection()
  if index not in range(self.exportFormat.GetCount()):
   return None
  else:
   return self.exportFormat.GetClientData(index)

 def saveAs_click(self, evt):
  self.saveAsDlg.SetPath(self.filename.GetValue())
  filterIndex = 0
  exporterClass = self.GetExporterClass()
  if exporterClass is not None and exporterClass.GetFileExtension() in self.fileFilters:
   filterIndex = self.fileFilters.index(exporterClass.GetFileExtension())
  self.saveAsDlg.SetFilterIndex(filterIndex)
  if self.saveAsDlg.ShowModal() == wx.ID_OK:
   filterIndex = self.saveAsDlg.GetFilterIndex()
   self.filename.SetValue(self.saveAsDlg.GetPath())
   for i in range(self.exportFormat.GetCount()):
    format = self.GetExporterClass(i)
    if format is not None and format.GetFileExtension() == self.fileFilters[filterIndex]:
     self.SetFormatIndex(i)
     break

 def format_changed(self, evt):
  self.dlg.CallHandlers('format', self.GetExporterClass())

 def SetFormatIndex(self, index):
  self.exportFormat.SetSelection(index)
  self.dlg.CallHandlers('format', self.GetExporterClass())
