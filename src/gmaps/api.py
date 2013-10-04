try:
 import json
except ImportError: #Not on python 26+.
  import simplejson as json
import urllib
import urllib2
from logger import logger
logging = logger.getChild('google_maps')

class GoogleMapsAPI(object):
 def __init__ (self, key="", url="http://maps.google.com/maps"):
  super(GoogleMapsAPI, self).__init__()
  self.key = key
  self.output = "json"
  self.sensor = "false"
  self.url = url
  self.decoder = json.decoder.JSONDecoder()
  self.accuracy_constants = (_('planet'), _('country'), _('region'), _('sub-region'), _('town'), _('post code'), _('street'), _('intersection'), _('address'), _('premise'))

 def Geocoding(self, q):
  data = {'q':q, 'output':self.output, 'sensor':self.sensor, 'key':self.key}
  url = "%s/geo" % self.url
  logging.debug(urllib.urlencode(data))
  response = urllib2.urlopen("%s?%s" % (url, urllib.urlencode(data)))
  logging.debug("Google maps response: %s" % str(response))
  answer = response.read()
  new = self.decoder.decode(answer)
  return new
