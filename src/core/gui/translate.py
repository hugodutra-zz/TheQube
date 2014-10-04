# -*- coding: utf-8 -*-

import wx
from core.gui import SquareDialog
import config
import core.translator
import operator
from ctypes import windll
from locale import windows_locale

from logger import logger
logging = logger.getChild('core.gui.translate')

class TranslateDialog (SquareDialog):
 t = core.translator.Translator()

 def __init__(self, *args, **kwargs):
  if 'title' not in kwargs:
   kwargs['title'] = _("Translate")
  self.title = kwargs['title']
  super(TranslateDialog, self).__init__(style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  langs = sorted(self.t.get_languages(self.get_current_language()).items(), key=operator.itemgetter(1))
  self.langs_keys = [i[0] for i in langs]
  self.langs_values = [i[1] for i in langs]
  self.langs_keys.insert(0, '')
  self.langs_values.insert(0, _("Auto detect"))
  current_lang = self.langs_keys.index(self.get_current_language())
  self.source_lang_list = self.labeled_control(_("Source language:"), wx.ComboBox, choices=self.langs_values, style = wx.CB_READONLY)
  self.source_lang_list.SetSelection(0)
  self.target_lang_list = self.labeled_control(_("Destination language:"), wx.ComboBox, choices=self.langs_values, style = wx.CB_READONLY)
  self.target_lang_list.SetSelection(current_lang)
  self.finish_setup()

 def get_current_language(self):
  """ Gets current language based on the configuration setting and normalizes it so it can be used with the Translator API."""
  if config.main['languages']['current'] == 'Windows':
   LCID = windll.kernel32.GetUserDefaultUILanguage()
   lang = windows_locale[LCID]
  else:
   lang = config.main['languages']['current']
  # And here begins the magic...
  all_langs = self.t.get_languages().keys()
  if lang in all_langs:
   curr_lang = lang
  else:
   if lang.split('_')[0] in all_langs:
    curr_lang = lang.split('_')[0]
   else:
    logging.Warn("Translator: unable to detect current language. Falling back to English.")
    curr_lang = 'en'
  return curr_lang
