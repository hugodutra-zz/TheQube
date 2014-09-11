import core
import wx

def set_wx_language(lang, locale_path):
 wx_locale = wx.Locale()
 wx_locale.AddCatalogLookupPathPrefix(locale_path)
 if '_' in lang:
  wx_lang = lang.split('_')[0]
 else:
  wx_lang = lang
 try:
  wx_locale.Init(lang, wx_lang)
 except:
  pass
