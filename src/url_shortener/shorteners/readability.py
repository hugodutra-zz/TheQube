# -*- encoding: utf-8 -*-

import requests
import json

from url_shortener import URLShortener
from logger import logger
logging = logger.getChild("core.UrlShorteners.Readability")

class ReadabilityShortener (URLShortener):
 api_url = "http://www.readability.com/api/shortener/v1/urls/"

 def __init__ (self, *args, **kwargs):
  self.name = "readability"
  return super(ReadabilityShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  params = {'url': url}
  response = requests.post(self.api_url, data=params)
  if response.ok:
   try:
    data = response.json()
   except ValueError as e:
    logging.exception("Value error upon shortening the URL: {}: {}".format(url, e))
   return data['meta']['rdd_url']
  else: # Response is not OK
   logging.exception("Bad response on shortening URL {}: {}".format(url, response.status_code))




 def created_url (self, url):
  return 'rdd.me' in url
