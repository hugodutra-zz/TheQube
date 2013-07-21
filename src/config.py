from logger import logger
logging = logger.getChild('core.config')

from configuration import Configuration, ConfigurationResetException
from paths import app_path, data_path

MAINFILE = "Main.conf"
MAINSPEC = "Main.defaults"

main = None

def setup ():
 global main
 try:
  main = Configuration(data_path(MAINFILE), app_path(MAINSPEC))
 except ConfigurationResetException:
  import output
  output.speak("Unable to load configuration file. Loading default configuration instead.", 0)
