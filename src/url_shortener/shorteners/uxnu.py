# -*- encoding: utf-8 -*-

import requests
import json

from url_shortener import URLShortener
from logger import logger
logging = logger.getChild("core.UrlShorteners.UxNu")

class UxnuShortener (URLShortener):
 api_url = "http://ux.nu/api/short"

 def __init__ (self, *args, **kwargs):
  self.name = "ux.nu"
  return super(UxnuShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  params = {'url': url}
  response = requests.get(self.api_url, params=params)
  if response.ok:
   try:
    data = response.json()
   except ValueError as e:
    logging.exception("Value error upon shortening the URL: {}: {}".format(url, e))
   return data['data']['url']
  else: # Response is not OK
   logging.exception("Bad response on shortening URL {}: {}".format(url, response.status_code))

 def created_url (self, url):
  return 'ux.nu' in url
