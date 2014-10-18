# -*- encoding: utf-8 -*-

import requests
import json

from url_shortener import URLShortener
from logger import logger
logging = logger.getChild("core.UrlShorteners.SentaLa")

class SentalaShortener (URLShortener):
 api_url = "http://senta.la/api.php"

 def __init__ (self, *args, **kwargs):
  self.name = "senta.la"
  return super(SentalaShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  params = {'dever': 'encurtar', 'format': 'simple', 'url': url}
  response = requests.get(self.api_url, params=params)
  if response.ok:
   return response.text.strip()
  else: # Response is not OK
   logging.exception("Bad response on shortening URL {}: {}".format(url, response.status_code))




 def created_url (self, url):
  return 'senta.la' in url
