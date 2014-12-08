# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('core.buffers.messages')

import misc
import output
import sessions
import time

from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.buffers.buffers.buffer import Buffer
from core.sessions.buffers import field_metadata as meta

class Messages (Buffer):
 """Base class providing all the generic things buffers that hold messages (Tweets, texts, etc.) require."""

 def __init__(self, *args, **kwargs):
  super(Messages, self).__init__(*args, **kwargs)
  self.set_field('when', _("Relative Time"), (self.item_timestamp, self.relative_time), filter=False)
  self.set_field('date', _("Date"), (self.item_timestamp, self.actual_date), filter=False)
  self.set_field('time', _("Time"), (self.item_timestamp, self.actual_time), filter=False)

 @staticmethod
 def relative_time (timestamp):
  from utils.time_period import TimePeriod
  if timestamp is None:
   return _("Not Available")
  now=time.time()
  delta = TimePeriod(now - timestamp)
  return _("{0} ago").format(delta)

 @staticmethod
 def actual_time (timestamp):
  if timestamp is None:
   return _("Not Available")
  #Format time according to locale settings.
  when = time.strftime('%X', time.localtime(timestamp))
  return when

 @staticmethod
 def actual_date (timestamp):
  if timestamp is None:
   return _("Not Available")
  #Format date according to locale settings.
  when = time.strftime('%x', time.localtime(timestamp))
  return when

 @staticmethod
 def user_local_time (offset):
  if offset is None:
   return _("Not Available")
  #Format offset time for locale
  when = time.time() + offset
  when = time.strftime('%X', time.gmtime(when))
  return when

 @staticmethod
 def user_local_date (offset):
  if offset is None:
   return _("Not Available")
  #Format offset date for locale
  when = time.time() + offset
  when = time.strftime('%x', time.gmtime(when))
  return when

 @buffer_defaults
 def item_timestamp (self, index=None, item=None):
  """Generic method buffers should provide to expose the current item's timestamp.
  Timestamp should be standard unix."""
  raise NotImplementedError

 def standardize_timestamp (self, timestamp):
  raise NotImplementedError

 @buffer_defaults
 def get_text (self, index=None, item=None):
  raise NotImplementedError

 @buffer_defaults
 def get_urls(self, index=None, item=None):
  try:
   urls = misc.find_urls(self.get_text(index, item))
  except:
   urls = []
  return urls

 @buffer_defaults
 def interact (self, index=None):
  """Opens the first URL in a Twitter item. Currently does not work if the only URL is a Twitter username.

"""

  urls = self.get_urls(index)
  if not urls:
   logging.debug("No web addresses or usernames in current item.")
   return output.speak(_("No URLs detected in current item."), True)
  url = urls[0]
  output.speak(_("Opening URL: %s" % url), True)
  logging.debug("Opening URL: %s" % url)
  misc.open_url_in_browser(url)

 def speak_index(self):
  answer = _("%s %d of %d.") % (self.item_name, len(self) - self.index, len(self))
  output.speak(answer)

