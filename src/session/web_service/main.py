from time import sleep
from urllib2 import urlopen, URLError
import output
import threading

from core.sessions.session import Session

class WebService (Session):
 """Abstract class to inherit from for useful functionality shared by sessions which access web services"""

 def __init__(self, *args, **kwargs):
  self.online = False
  self.API_initialized_event = threading.Event()
  super(WebService, self).__init__(*args, **kwargs)

 def API_initialized(self):
  self.online = True
  self.API_initialized_event.set()

 def wait_for_availability (self, url, message, delay=1, retries=0):
  """Attempts to connect to the provided URL.  If it cannot, continues trying retries times (defaulting to an infinite retry if retries is left at 0) every delay seconds, speaking the provided message after the first failure.  Returns true once connected."""
  count = 0
  while not retries or count <= retries:
   try:
    addinfo = urlopen(url)
    addinfo.close()
    return True
   except URLError:
    if not count:
     output.speak(_(message), True)
   count += 1
   sleep(delay)

 def is_online (self):
  #Return a boolean indicating if a connection to the Internet is available.
  raise NotImplementedError

