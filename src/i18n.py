from logger import logger
logging = logger.getChild("core.i18n")

import application
import config
from i18n_utils import core, wx_i18n
import paths



def setup():
 logging.info("Initializing the i18n subsystem.")
 core.set_active_language(application.name, paths.locale_path(), config.main['languages']['current'])
 #wx_i18n.set_wx_language(config.main['languages']['current'], paths.locale_path())

def available_languages():
 return core.available_languages(paths.locale_path(), application.name)

def printable_lang(lang):
 return lang['language']

def printable_available_languages():
 langs = available_languages()
 return [printable_lang(langs[i]) for i in langs]

def lang_from_printable_language(language):
 langs = available_languages()
 for i in langs:
  if langs[i]['language'] == language:
   return i #I know it's just the key

