import logging as original_logging
logging = original_logging.getLogger('core.misc')

import paths
import re
import platform
import sys
import webbrowser

from ctypes import Structure, windll, c_uint, sizeof, byref

def SecondsToString(seconds, precision=0):
 hour = seconds // 3600
 min = (seconds // 60) % 60
 sec = seconds - (hour * 3600) - (min * 60)
 sec_spec = "." + str(precision) + "f"
 sec_string = sec.__format__(sec_spec)
 string = ""
 if (hour == 1):
  string += "%d hour, " % hour
 elif (hour >= 2):
  string += "%d hours, " % hour
 if (min == 1):
  string += "%d minute, " % min
 elif (min >= 2):
  string += "%d minutes, " % min
 if (sec == 1):
  string += "%s second" % sec_string
 else:
  string += "%s seconds" % sec_string
 return string

def url_cleanup(url):
 logging.debug("url_cleanup, start: %s" % (url))
 url = url.replace("-http", " http")
 url = url.replace("-www", " www")
 url = url.replace("-https", " https")
 if url.startswith("(") or url.startswith('"'):
  url = url[1:]
 if url[-1] in [":", ".", ",", "?", "!", ")", '"']:
  url = url[:-1]
 elif url.endswith("'s"):
  url = url[:-2]
 logging.debug("url_cleanup, end: %s" % (url))
 return url

def RemoveDuplicates(l, transform = None):
 if not transform:
  def transform(x):
   return x
 seen = {}
 result = []
 for item in l:
  marker = transform(item)
  if marker in seen:
   continue
  seen[marker] = True
  result.append(item)
 return result

def import_durus():
 old_stdout = sys.stdout
 old_stderr = sys.stderr
 sys.stdout = sys.__stdout__
 sys.stderr = sys.__stderr__
 from durus import logger
 logger.direct_output(open(paths.data_path('durus.log'), 'w'))
 sys.stdout = old_stdout
 sys.stderr = old_stderr
 from durus.file_storage import FileStorage
 from durus.connection import Connection
 return (FileStorage, Connection)

def find_urls (string):
 removed = '\'\\.,[](){}:;"'
 r = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
 return [s.strip(removed) for s in r.findall(string)]

def GetLastInputInfo():
 class LastInputInfo(Structure):
  _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]
 last_input_info = LastInputInfo()
 last_input_info.cbSize = sizeof(last_input_info)
 windll.user32.GetLastInputInfo(byref(last_input_info))
 return last_input_info.dwTime

def GetTickCount():
 return windll.kernel32.GetTickCount()

def approximate_time(timespan):
 times_dict = {
  (0, 1): _("less than %d second"),
  (1, 2): _("%d second"),
  ( 2, 59): _("%d seconds"),
  (60, 119): _("%d minute"),
  (120, 3599): _("%d minutes"),
  (3600, 7199): _("%d hour"),
  (7200, 86399): _("%d hours"),
  (86400, 172799): _("%d day"),
  (172800, 604799): _("%d days"),
  (604800, 1290599): _("%d week"),
  (1290600, 2591999): _("%d weeks"),
  (2592000, 5183999): _("%d month"),
  (5184000, 31535999): _("%d months"),
  (31536000, 63071999): _("%d year"),
  (63072000, sys.maxint): _("%d years")
 }
 for k in times_dict:
  if timespan >= k[0] and timespan <= k[1]:
   return times_dict[k] % (timespan/k[0])

def open_url_in_browser(url):
 if platform.system() == 'Windows':
  browser = webbrowser.get('windows-default')
 else:
  browser = webbrowser
 browser.open_new_tab(url)
