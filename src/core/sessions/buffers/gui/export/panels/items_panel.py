import wx
from core.sessions.buffers.gui.export import ExportPanel
import sessions
from core.sessions.buffers.exporter.exporters import RANGE_ALL, RANGE_ALL_REVERSED, RANGE_CUSTOM
import signals
from pydispatch import dispatcher

class ItemsPanel (ExportPanel):
 def __init__(self, *args, **kwargs):
  super(ItemsPanel, self).__init__(pageName = _("Items"), *args, **kwargs)
  self.buffer_label = wx.StaticText(self, label = _("Buffer"))
  self._first = self.buffer = wx.ComboBox(self, style = wx.CB_READONLY | wx.CB_SORT)
  self.buffer.SetSizerProps(expand = True)
  self.buffer.Bind(wx.EVT_COMBOBOX, self.buffer_changed)
  self.item_template_label = wx.StaticText(self, label = _("Item template"))
  self.item_template = wx.TextCtrl(self)
  self.item_template.SetSizerProps(expand = True)
  self.range_type_label = wx.StaticText(self, label = _("Range"))
  self.range_type = wx.ComboBox(self, style = wx.CB_READONLY, choices = [_("All (bottom to top)"), _("All (top to bottom)"), _("Custom")])
  self.range_type.SetSizerProps(expand = True)
  self.range_type.Bind(wx.EVT_COMBOBOX, self.range_type_changed)
  self.first_index_label = wx.StaticText(self, label = _("First item index"))
  self.first_index = wx.SpinCtrl(self, min = 1, max = 1, initial = 1)
  self.first_index.SetSizerProps(expand = True)
  self.last_index_label = wx.StaticText(self, label = _("Last item index"))
  self.last_index = wx.SpinCtrl(self, min = 1, max = 1, initial = 1)
  self.last_index.SetSizerProps(expand = True)
  self.range_enabled = False
  self.last_buffer = None
  self.max_index = 1
  self.finish_setup()
  self.dlg.AddHandler('format', self.HandleFormatChange)
  self.dlg.AddHandler('buffer', self.HandleBufferChange)
  self.dlg.AddHandler('range_type', self.HandleRangeTypeChange)
  self.empty_buffers = []
  with self.dlg.session.storage_lock:
   dispatcher.connect(self.AddNewBuffer, signals.buffer_created, self.dlg.session)
   for buffer in self.dlg.session.buffers:
    if buffer and buffer.get_flag('exportable'):
     self.AddNewBuffer(buffer)

 def get_buffer(self, index = None):
  if index is None:
   index = self.buffer.GetSelection()
  if not self.buffer.Shown or index not in range(self.buffer.GetCount()):
   return None
  else:
   return self.buffer.GetClientData(index)
 
 def set_bufferIndex(self, index):
  self.buffer.SetSelection(index)
  self.dlg.CallHandlers('buffer', self.get_buffer())
 
 def GetRangeType(self):
  range_type = self.range_type.GetSelection()
  if not self.range_type.Shown or range_type not in (RANGE_ALL, RANGE_ALL_REVERSED, RANGE_CUSTOM):
   range_type = None
  return range_type
 
 def SetRangeType(self, newRangeType):
  self.range_type.SetSelection(newRangeType)
  self.dlg.CallHandlers('range_type', self.GetRangeType())

 def GetExportArgs(self):
  kwargs = {}
  if self.buffer.Shown:
   kwargs['buffer'] = self.get_buffer()
  if self.item_template.Shown:
   kwargs['item_template'] = self.item_template.GetValue()
  if self.range_type.Shown:
   kwargs['range_type'] = self.GetRangeType()
   if kwargs['range_type'] == RANGE_CUSTOM:
    kwargs['first'] = self.max_index - self.first_index.GetValue()
    kwargs['last'] = self.max_index - self.last_index.GetValue()
  return kwargs

 def buffer_changed(self, evt):
  self.dlg.CallHandlers('buffer', self.get_buffer())

 def range_type_changed(self, evt):
  self.dlg.CallHandlers('range_type', self.GetRangeType())

 def HandleFormatChange(self, format):
  supportedArgs = {}
  if format is not None:
   supportedArgs = format.GetSupportedArgs()
  self.range_enabled = 'range' in supportedArgs
  bufferPrevShown = self.buffer.Shown
  self.buffer_label.Shown = self.buffer.Shown = 'buffer' in supportedArgs
  self.item_template_label.Shown = self.item_template.Shown = 'item_template' in supportedArgs
  if bufferPrevShown != self.buffer.Shown:
   self.dlg.CallHandlers('buffer', self.get_buffer())
  if self.buffer.Shown and self.range_enabled != self.range_type.Shown:
   self.range_type_label.Shown = self.range_type.Shown = True
   self.dlg.CallHandlers('range_type', self.GetRangeType())
  if self.get_buffer() is None and self.buffer.Shown and self.buffer.GetCount() > 0:
   self.set_bufferIndex(0)
  if self.GetRangeType() is None and self.range_type.Shown:
   self.SetRangeType(RANGE_ALL)
  if 'buffer' not in supportedArgs and 'range' not in supportedArgs and 'item_template' not in supportedArgs:
   self.ShowPage(False)
  else:
   self.ShowPage(True)

 def HandleBufferChange(self, buffer):
  rangePrevShown = self.range_type.Shown
  if buffer is None or len(buffer) == 0:
   self.range_type_label.Shown = self.range_type.Shown = False
   self.item_template.SetValue("")
  else:
   if self.range_enabled and self.range_enabled != self.range_type.Shown:
    self.range_type_label.Shown = self.range_type.Shown = True
   if buffer is not self.last_buffer:
    self.item_template.SetValue(buffer.get_template())
    self.max_index = len(buffer)
    self.first_index.SetRange(1, self.max_index)
    self.last_index.SetRange(1, self.max_index)
    self.first_index.Value = 1
    self.last_index.Value = self.max_index
  if rangePrevShown != self.range_type.Shown:
   self.dlg.CallHandlers('range_type', self.GetRangeType())
  self.last_buffer = buffer
 
 def HandleRangeTypeChange(self, range_type):
  self.first_index_label.Shown = self.first_index.Shown = range_type == RANGE_CUSTOM
  self.last_index_label.Shown = self.last_index.Shown = range_type == RANGE_CUSTOM

 def get_buffer_index(self, buffer = None):
  if buffer is None:
   index = self.buffer.GetSelection()
  else:
   index = wx.NOT_FOUND
   for i in range(self.buffer.GetCount()):
    if buffer is self.buffer.GetClientData(i):
     index = i
     break
  return index

 def remove_buffer(self, buffer, fromList = False, fromUI = False):
  if fromUI and fromList:
   dispatcher.disconnect(self.HandleDismissBuffer, signals.dismiss_buffer, buffer)
   dispatcher.disconnect(self.HandleNewPosts, signals.buffer_updated, buffer)
   dispatcher.disconnect(self.HandleClearBuffer, signals.clear_buffer, buffer)
   dispatcher.disconnect(self.Handleremove_item, signals.remove_item, buffer)
  if fromUI:
   index = self.get_buffer_index(buffer)
   if index != wx.NOT_FOUND:
    self.buffer.Delete(index)
    self.dlg.CallHandlers('buffer', self.get_buffer())
  if fromList:
   if buffer in self.empty_buffers:
    self.empty_buffers.remove(buffer)

 def HandleDismissBuffer(self, sender):
  self.remove_buffer(sender, fromUI = True, fromList = True)

 def HandleNewPosts(self, sender, posts = []):
  if sender in self.empty_buffers and len(posts) > 0:
   self.remove_buffer(sender, fromList = True)
   self.buffer.Append(sender.name, sender)
  elif sender is self.get_buffer():
   self.max_index += len(posts)
   self.first_index.SetRange(1, self.max_index)
   self.first_index.Value += len(posts)
   self.last_index.SetRange(1, self.max_index)
   self.last_index.Value += len(posts)

 def HandleClearBuffer(self, sender):
  self.remove_buffer(sender, fromUI = True)
  if sender not in self.empty_buffers:
   self.empty_buffers.append(sender)

 def Handleremove_item(self, sender, post):
  if len(sender) == 0:
   self.HandleClearBuffer(sender)
  elif sender is self.get_buffer():
   self.max_index -= 1
   if self.first_index.Value > self.max_index:
    self.first_index.Value = self.max_index
   if self.last_index.Value > self.max_index:
    self.last_index.Value = self.max_index
   self.first_index.SetRange(1, self.max_index)
   self.last_index.SetRange(1, self.max_index)

 def AddNewBuffer(self, buffer):
  if buffer.get_flag('exportable'):
   dispatcher.connect(self.HandleDismissBuffer, signals.dismiss_buffer, buffer)
   dispatcher.connect(self.HandleNewPosts, signals.buffer_updated, buffer)
   dispatcher.connect(self.HandleClearBuffer, signals.clear_buffer, buffer)
   dispatcher.connect(self.Handleremove_item, signals.remove_item, buffer)
   if len(buffer) == 0:
    self.empty_buffers.append(buffer)
   else:
    self.buffer.Append(buffer.name, buffer)

 def Destroy(self):
  dispatcher.disconnect(self.AddNewBuffer, signals.buffer_created, self.dlg.session)
  buffers = []
  buffers.extend(self.empty_buffers)
  buffers.extend([self.get_buffer(i) for i in range(self.buffer.GetCount())])
  buffers = set(buffers)
  for buffer in buffers:
   self.remove_buffer(buffer, fromUI = True, fromList = True)
  super(ItemsPanel, self).Destroy()
