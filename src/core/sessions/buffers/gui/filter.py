import sessions
import wx

from core.gui import SquareDialog
from copy import deepcopy
from core.sessions.buffers import field_metadata as meta

class FilterDialog (SquareDialog):
 """The UI for performing a filter operation."""

 def __init__(self, text="", buffer=None, *args, **kwargs):

  super(FilterDialog, self).__init__(title=_("Filter: %s") % buffer.display_name, *args, **kwargs)
  fields = buffer.get_item_metadata()
  #First Row
  wx.StaticText(parent=self.pane, label=_("Filters:"))
  self.filters = wx.ListBox(self.pane)
  self.filters.SetSizerProps(expand=True)
  self.filters.Bind(wx.EVT_LISTBOX, self.change_filters)
  self.addFilter = wx.Button(self.pane, label=_("&Add"))
  self.addFilter.Bind(wx.EVT_BUTTON, self.add_filter)
  self.removeFilter = wx.Button(self.pane, label=_("&Remove"))
  self.removeFilter.Bind(wx.EVT_BUTTON, self.remove_filter)
  self.useRegex = wx.CheckBox(parent=self.pane, label=_("Use a regular expression"))
  self.useRegex.SetSizerProps(expand=True)
  self.useRegex.Bind(wx.EVT_CHECKBOX, self.update_useRegex)
  self.termLabel = wx.StaticText(parent=self.pane, label=_("Buffer Search:"))
  self.term = wx.TextCtrl(parent=self.pane, value=text)
  self.term.SetSizerProps(expand=True)
  self.term.Bind(wx.EVT_TEXT, self.update_term)
  self.fieldsLabel = wx.StaticText(parent=self.pane, label=_("Fields:"))
  self.fields = wx.ListBox(self.pane, style=wx.LB_MULTIPLE | wx.LB_SORT)
  self.fields.SetSizerProps(expand=True)
  self.fields.Bind(wx.EVT_LISTBOX, self.update_fields)
  for (field_name, field) in fields.iteritems():
   if field.filter and field.field_type == meta.FT_TEXT:
    self.fields.Append(field.display_name, field_name)
  if self.fields.GetCount() < 2:
   self.fieldsLabel.Hide()
   self.fields.Hide()
  self.remove = wx.CheckBox(parent=self.pane, label=_("excluding"))
  self.remove.SetSizerProps(expand=True)
  self.remove.Bind(wx.EVT_CHECKBOX, self.update_remove)
  self.replace = wx.CheckBox(parent=self.pane, label=_("Replace source buffer"))
  self.replace.Bind(wx.EVT_CHECKBOX, self.update_replace)
  self.finish_setup()
  self.add_filter()

 def update_UI(self):
  enable = self.filters.GetSelection() != wx.NOT_FOUND
  if self.filters.GetCount() > 0:
   last_spec = self.filters.GetClientData(self.filters.GetCount() - 1)
   self.addFilter.Enable(len(last_spec['term']) != 0)
  if self.filters.GetCount() > 1:
   self.removeFilter.Enable(enable)
  else:
   self.removeFilter.Enable(False)
  self.useRegex.Enable(enable)
  self.termLabel.Enable(enable)
  self.term.Enable(enable)
  self.remove.Enable(enable)
  self.replace.Enable(enable)
  self.fieldsLabel.Enable(enable)
  self.fields.Enable(enable)
 
 def get_filter_specs(self):
  return [self.filters.GetClientData(i) for i in range(self.filters.GetCount())]
 
 def get_selected_spec(self):
  cursel = self.filters.GetSelection()
  if cursel == wx.NOT_FOUND:
   return None
  else:
   return self.filters.GetClientData(cursel)

 def update_useRegex(self, evt=None, UI=False):
  spec = self.get_selected_spec()
  if spec is None:
   return
  if UI:
   self.useRegex.SetValue(spec['useRegex'])
  else:
   spec['useRegex'] = self.useRegex.GetValue()
   self.update_filter_description()
  if spec['useRegex']:
   self.termLabel.LabelText = _("Regular Expression:")
  else:
   self.termLabel.LabelText = _("Term:")
  
 def update_remove(self, evt=None, UI=False):
  spec = self.get_selected_spec()
  if spec is None:
   return
  if UI:
   self.remove.SetValue(spec['remove'])
  else:
   spec['remove'] = self.remove.GetValue()
   self.update_filter_description()
 
 def update_replace(self, evt=None, UI=False):
  spec = self.get_selected_spec()
  if spec is None:
   return
  if UI:
   self.replace.SetValue(spec['replace'])
  else:
   spec['replace'] = self.replace.GetValue()
   self.update_filter_description()

 def update_term(self, evt=None, UI=False):
  spec = self.get_selected_spec()
  if spec is None:
   return
  if UI:
   self.term.ChangeValue(spec['term'])
  else:
   spec['term'] = self.term.GetValue()
   self.update_filter_description()
   self.update_UI()

 def update_fields(self, evt=None, UI=False):
  spec = self.get_selected_spec()
  if spec is None:
   return
  if UI:
   for i in range(self.fields.GetCount()):
    if self.fields.GetClientData(i) in spec['fields']:
     self.fields.Select(i)
    else:
     self.fields.Deselect(i)
  else:
   spec['fields'] = [self.fields.GetClientData(i) for i in self.fields.GetSelections()]

 def change_filters(self, evt=None):
  self.update_useRegex(UI=True)
  self.update_term(UI=True)
  self.update_fields(UI=True)
  self.update_remove(UI=True)
  self.update_replace(UI=True)
  self.update_UI()

 def add_filter(self, evt=None):
  spec = self.get_selected_spec()
  if spec is None:
   new_spec = {'term':"", 'useRegex':False, 'remove':False, 'replace':False, 'fields':[]}
  else:
   new_spec = deepcopy(spec)
   new_spec['term'] = ""
  #Filter items are created with a place holder of <new filter>, do not localize.
  pos = self.filters.Append("<new filter>", clientData=new_spec)
  self.filters.SetSelection(pos)
  self.update_filter_description()
  self.change_filters()
  self.term.SetFocus()
 
 def remove_filter(self, evt=None):
  pos = self.filters.GetSelection()
  self.filters.Delete(pos)
  if pos >= self.filters.GetCount():
   pos = self.filters.GetCount() - 1
  self.filters.SetSelection(pos)
  self.change_filters()
  self.filters.SetFocus()
 
 def update_filter_description(self):
  spec = self.get_selected_spec()
  pos = self.filters.GetSelection()
  if spec is None or pos == wx.NOT_FOUND:
   return
  desc = ""
  if spec['replace']:
   desc += _("replacement ")
  if spec['remove']:
   desc += _("without ")
  else:
   desc += _("with ")
  if spec['useRegex']:
   desc += _("RX ")
  desc += spec['term']
  self.filters.SetString(pos, desc)
