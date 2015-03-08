# -*- encoding: utf-8 -*-

import requests
import json

from url_shortener import URLShortener
from logger import logger
logging = logger.getChild("core.UrlShorteners.QpsRu")

class QpsruShortener (URLShortener):
 api_url = "http://qps.ru/api"

 def __init__ (self, *args, **kwargs):
  self.name = "qps.ru"
  return super(QpsruShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  params = {'url': url}
  response = requests.get(self.api_url, params=params)
  if response.ok:
   return response.text.strip()
  else: # Response is not OK
   logging.exception("Bad response on shortening URL {}: {}".format(url, response.status_code))




 def created_url (self, url):
  return 'qps.ru' in url
