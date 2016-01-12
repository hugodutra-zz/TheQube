# -*- coding: utf-8 -*-

import wx
from core.gui import SquareDialog
import config
import core.goslate
import operator
from ctypes import windll
from locale import windows_locale
from BeautifulSoup import BeautifulStoneSoup

from logger import logger
logging = logger.getChild('core.gui.translate')

class TranslateDialog (SquareDialog):
 t = core.goslate.Goslate()
 LCID = windll.kernel32.GetUserDefaultUILanguage()
 win_lang = windows_locale[LCID]

 def __init__(self, *args, **kwargs):
  if 'title' not in kwargs:
   kwargs['title'] = _("Translate")
  self.title = kwargs['title']
  super(TranslateDialog, self).__init__(style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, *args, **kwargs)
  if not hasattr(self, 'langs'):
   self.langs = sorted(self.t.get_languages(self.get_current_language()).items(), key=operator.itemgetter(1))
  if not hasattr(self, 'langs_keys'):
   self.langs_keys = [i[0] for i in self.langs]
   self.langs_keys.insert(0, '')
  if not hasattr(self, 'langs_values'):
   self.langs_values = [i[1] for i in self.langs]
   # Preventing the translator from spitting out HTML entities
   self.langs_values = [unicode(BeautifulStoneSoup(n, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)) if n.startswith(u"&#") else n for n in self.langs_values]
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
   lang = self.win_lang
  else:
   lang = config.main['languages']['current']
  # And here begins the magic...
  if not hasattr(self, 'all_langs'):
   self.all_langs = self.t.get_languages().keys()
  if lang in self.all_langs:
   curr_lang = lang
  else:
   if lang.split('_')[0] in self.all_langs:
    curr_lang = lang.split('_')[0]
   else:
    logging.Warn("Translator: unable to detect current language. Falling back to English.")
    curr_lang = 'en'
  return curr_lang
