import wx
from core.gui import SquareDialog
import google_apis.translate as t

class TranslateDialog (SquareDialog):

 def available_languages(self):
  l = t._languages.keys()
  d = t._languages.values()
  l.insert(0, '')
  d.insert(0, _("Auto detect"))
  return sorted(zip(l, d))

 def __init__(self, *args, **kwargs):
  if 'title' not in kwargs:
   kwargs['title'] = _("Translate")
  self.title = kwargs['title']
  super(TranslateDialog, self).__init__(style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  self.source_lang_list = self.labeled_control(_("Source language:"), wx.ComboBox, choices=[x[1] for x in self.available_languages()], style = wx.CB_READONLY)
  self.source_lang_list.SetSelection(0)
  self.target_lang_list = self.labeled_control(_("Destination language:"), wx.ComboBox, choices=[x[1] for x in self.available_languages()], style = wx.CB_READONLY)
  self.target_lang_list.SetSelection(18)
  self.finish_setup()
