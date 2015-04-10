# -*- encoding: utf-8 -*-

import requests
import json

from url_shortener import URLShortener
from logger import logger
logging = logger.getChild("core.UrlShorteners.GooGl")

class GooglShortener (URLShortener):
 api_url = "https://www.googleapis.com/urlshortener/v1/url"

 def __init__ (self, *args, **kwargs):
  self.name = "goo.gl"
  return super(GooglShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  params = json.dumps({'longUrl': url}, ensure_ascii=False)
  headers = {'content-type': 'application/json'}
  response = requests.post(self.api_url, data=params, headers=headers)
  if response.ok:
   try:
    data = response.json()
   except Exception as e:
    logging.exception("Unable to retrieve json upon shortening the URL: {}; exception: {}".format(url, e))
   if 'id' in data:
    return data['id']
  else: # Response is not OK
   logging.exception("Bad response on shortening URL {}: {}".format(url, str(response)))




 def created_url (self, url):
  return 'goo.gl' in url
