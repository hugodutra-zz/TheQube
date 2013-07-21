from logger import logging
import httplib
import oauth2
import time
from urlparse import urlsplit
import json


class UserStreamer(object):

 def __init__(self, consumer=None, token=None, url='https://userstream.twitter.com/1.1/user.json', callback=None, reconnected_callback=None, retry_delay=5):
  self.consumer = consumer
  self.token = token
  self.url = url
  self.connection = None
  self.response = None
  self.connected = False
  self.buffer = ""
  self.callback = callback or self.print_item
  self.reconnected_callback = reconnected_callback
  self.retry_delay = retry_delay
  self.connect_times = 0

 @staticmethod
 def print_item(item):
  print item

 def stream(self):
  while True:
   try:
    if not self.response:
     self.create_connection()
     if self.connect_times > 1 and callable(self.reconnected_callback):
      try:
       self.reconnected_callback()
      except:
       time.sleep(self.retry_delay)
    self.perform_read()
   except:
    time.sleep(self.retry_delay)
    self.response = None
    self.reconnecting = True
  self.connected = False

 def perform_read(self):
  new = self.response.read(1)
  self.buffer += new
  if self.buffer.endswith('\r\n') and self.buffer.strip():
   self.load_from_buffer()

 def load_from_buffer(self):
  loaded = json.loads(self.buffer.strip())
  self.buffer = ""
  try:
   self.callback(loaded)
  except:
   pass


 def create_connection(self):
  self.connection = httplib.HTTPSConnection(urlsplit(self.url).netloc, timeout=self.retry_delay*10)
  headers = sign_request(self.consumer, self.token, self.url)
  self.connection.request('GET', self.url, headers=headers)
  self.response = self.connection.getresponse(True)
  self.connected = True
  self.connect_times += 1

def sign_request(consumer, token, url, method='GET', headers={}, parameters={}, sigmethod=None):
 sigmethod = sigmethod or oauth2.SignatureMethod_HMAC_SHA1()
 oauth_request = oauth2.Request.from_consumer_and_token(consumer, http_url=url, http_method=method, token=token, parameters=parameters)
 oauth_request.sign_request(sigmethod, consumer, token)
 headers.update(oauth_request.to_header())
 return headers


def test():
 s = UserStreamer()
 s.connect()
