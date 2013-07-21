from logger import logger
logging = logger.getChild('sessions.twitter.buffers.main')

from pydispatch import dispatcher
from core.sessions.buffers.buffer_defaults import buffer_defaults

import calendar
import config
import html_filter
import misc
import output
import re
import rfc822
import signals
import time
import wx
from utils.wx_utils import question_dialog
from conditional_template import ConditionalTemplate as Template

from core.sessions.buffers.buffers import Updating
from core.sessions.storage.buffers.storage import Storage
from core.sessions.sound.buffers.audio import Audio
from api_count import APICount
from core.sessions.buffers import field_metadata as meta

class Twitter (Updating, Storage, Audio, APICount):
 """Parent twitter buffer class."""

 def __init__ (self, *args, **kwargs):
  super(Twitter, self).__init__(*args, **kwargs)
  self.set_flag('deletable', False)
  self.set_flag('temp', False)
  self.set_flag('filterable', True)
  self.set_flag('exportable', True)

 @staticmethod
 def _twitter_id_compare(x, y):
  if x['id'] > y['id']:
   return 1
  elif x['id'] == y['id']:
   return 0
  else:
   return -1

 @staticmethod
 def standardize_timestamp(date):
  if date is None:
   return None
  return calendar.timegm(rfc822.parsedate(date))

 def process_update(self, update, *args, **kwargs):
  update = self.find_new_data (update)
  update.reverse()
  for i in update:
   if 'text' in i:
    i['text'] = html_filter.StripChars(i['text'])
    i['text'] = i['text'].replace('\n', ' ')
   if 'retweeted_status' in i and 'text' in i['retweeted_status']:
    i['retweeted_status']['text'] = html_filter.StripChars(i['retweeted_status']['text'])
    i['retweeted_status']['text'] = i['retweeted_status']['text'].replace('\n', ' ')
  return update

 def process_source(self, field):
  source = field
  if source is None:
   source = 'DM'
  source = html_filter.StripChars(source)
  if source.startswith("<a href"):
   source = source[:-4]
   source = source.split("\">")[1]
  return source

 @buffer_defaults
 def get_mentions (self, index=None):
  try:
   working = self.get_text(index)
  except:
   working = ""
  return re.findall('(?<![a-zA-Z0-9_])@([a-zA-Z0-9_]+)', working)

 def fetch_previous (self, *args, **kwargs):
  pass

 @buffer_defaults
 def get_hash_tags (self, index=None, item=None):
  try:
   working = self.get_text(index=index, item=item)
  except:
   working = ""
  return re.findall('(#[a-zA-Z0-9_\-]+)', working)

 @buffer_defaults
 def get_urls(self, index=None, item=None):
  res = super(Twitter, self).get_urls(index=index, item=item)
  user_ptr = self.get_user_info(index, item)
  if user_ptr and user_ptr['url'] and user_ptr['url'].lower() != 'http://none':
   res.append(user_ptr['url'])
  return res

 @buffer_defaults
 def format_user_info (self, index=None):
  user_ptr = self.get_user_info(index)
  if not user_ptr:
   return
  template = Template(self.session.config['templates']['user_info'])
  mapping = {}
  mapping['name'] = user_ptr['name']
  mapping['screen_name'] = user_ptr['screen_name']
  mapping['location'] = user_ptr['location']
  mapping['url'] = user_ptr['url']
  mapping['bio'] = user_ptr['description']
  mapping['followers_count'] = user_ptr['followers_count']
  mapping['friends_count'] = user_ptr['friends_count']
  mapping['tweets_count'] = user_ptr['statuses_count']
  mapping['when'] = self.relative_time(self.standardize_timestamp(user_ptr['created_at']))
  mapping['time'] = self.actual_time(self.standardize_timestamp(user_ptr['created_at']))
  mapping['date'] = self.actual_date(self.standardize_timestamp(user_ptr['created_at']))
  if user_ptr['utc_offset'] or user_ptr['utc_offset'] == 0:
   mapping['local_time'] = self.user_local_time(user_ptr['utc_offset'])
   mapping['local_date'] = self.user_local_date(user_ptr['utc_offset'])
  else:
   mapping['local_time'] = "not available"
   mapping['local_date'] = "not available"
  return template.Substitute(mapping)

 def get_next_item_time_step_index (self, step, index=None):
  if not index and index != 0:
   index = self.index
  step = step * 60
  new_index = len(self) - 1
  current_tweet_time = self.standardize_timestamp (self[index]['created_at'])
  for i in range(index+1, len(self)):
   if self.standardize_timestamp (self[i]['created_at']) - current_tweet_time >= step:
    new_index = i
    break
  return new_index

 def get_prev_item_time_step_index (self, step, index=None):
  if not index and index != 0:
   index = self.index
  step = step * 60
  new_index = 0
  current_tweet_time = self.standardize_timestamp (self[index]['created_at'])
  for i in range(index-1, -1, -1):
   if current_tweet_time - self.standardize_timestamp (self[i]['created_at']) >= step:
    new_index = i
    break
  return new_index

 @buffer_defaults
 def get_name(self, index=None, item=None):
  if 'user' in item and 'name' in item['user']:
   who = item['user']['name']
  elif 'sender' in item and 'name' in item['sender']:
   who = item['sender']['name']
  elif 'name' in item:
   who = item['name']
  else:
   logging.debug("Unable to find name in buffer %s, index %s, item %s" % (self.name, index, item))
   who = item['name']
  return who

 @buffer_defaults
 def get_screen_name(self, index=None, item=None):
  if 'user' in item and 'screen_name' in item['user']:
   who = item['user']['screen_name']
  elif 'sender' in item and 'screen_name' in item['sender']:
   who = item['sender']['screen_name']
  elif 'screen_name' in item:
   who = item['screen_name']
  elif item.has_key('from_user'):
   who = item['from_user']
  else:
   logging.exception("Unable to find screen name in buffer %s, index %s, item %s" % (self.name, index, item))
   who = item['screen_name']
  return who

 @buffer_defaults
 def get_text(self, index=None, item=None):
  if 'retweeted_status' not in item and 'text' in item:
   text = item['text']
  elif 'retweeted_status' in item and 'text' in item['retweeted_status']:
   text = "RT @%s: %s" % (item['retweeted_status']['user']['screen_name'], item['retweeted_status']['text'])
  else:
   logging.debug("Unable to find text in buffer %s, index %s, item %s" % (self.name, index, item))
  return text

 @buffer_defaults
 def get_user_info(self, index=None, item=None):
  if 'user' in item:
   user_ptr = item['user']
  elif 'sender' in item:
   user_ptr = item['sender']
  elif 'screen_name' in item:
   user_ptr = item
  else:
   logging.debug("Unable to find user information in buffer %s, index %s, item %s" % (self.name, index, item))
   return
  return user_ptr

 def process_users(self, items):
  users = self.session.users
  for (i, item) in enumerate(items):
# Tweets
   if 'user' in item:
    if unicode(item['user']['id']) not in users:
     with self.session.storage_lock: users[unicode(item['user']['id'])] = {}
    if '_last_update' not in users[unicode(item['user']['id'])] or time.mktime(rfc822.parsedate(item['created_at'])) > time.mktime(rfc822.parsedate(users[unicode(item['user']['id'])]['_last_update'])):
     item['user']['_last_update'] = item['created_at']
     with self.session.storage_lock: users[unicode(item['user']['id'])].update(item['user'])
    item['user'] = users[unicode(unicode(item['user']['id']))]
# Retweets
   if 'retweeted_status' in item and 'user' in item['retweeted_status']:
    if unicode(item['retweeted_status']['user']['id']) not in users:
     with self.session.storage_lock: users[unicode(item['retweeted_status']['user']['id'])] = {}
    if '_last_update' not in users[unicode(item['retweeted_status']['user']['id'])] or time.mktime(rfc822.parsedate(item['retweeted_status']['created_at'])) > time.mktime(rfc822.parsedate(users[unicode(item['retweeted_status']['user']['id'])]['_last_update'])):
     item['retweeted_status']['user']['_last_update'] = item['retweeted_status']['created_at']
     with self.session.storage_lock: users[unicode(item['retweeted_status']['user']['id'])].update(item['retweeted_status']['user'])
    item['retweeted_status']['user'] = users[unicode(item['retweeted_status']['user']['id'])]
# Direct messages
   if 'sender' in item:
    if unicode(item['sender']['id']) not in users:
     with self.session.storage_lock: users[unicode(item['sender']['id'])] = {}
    if '_last_update' not in users[unicode(item['sender']['id'])] or time.mktime(rfc822.parsedate(item['created_at'])) > time.mktime(rfc822.parsedate(users[unicode(item['sender']['id'])]['_last_update'])):
     item['sender']['_last_update'] = item['created_at']
     with self.session.storage_lock: users[unicode(item['sender']['id'])].update(item['sender'])
    item['sender'] = users[unicode(item['sender']['id'])]
   if 'recipient' in item:
    if unicode(item['recipient']['id']) not in users:
     with self.session.storage_lock: users[unicode(item['recipient']['id'])] = {}
    if '_last_update' not in users[unicode(item['recipient']['id'])] or time.mktime(rfc822.parsedate(item['created_at'])) > time.mktime(rfc822.parsedate(users[unicode(item['recipient']['id'])]['_last_update'])):
     item['recipient']['_last_update'] = item['created_at']
     with self.session.storage_lock: users[unicode(item['recipient']['id'])].update(item['recipient'])
    item['recipient'] = users[unicode(item['recipient']['id'])]
  return items

 @buffer_defaults
 def remove_item(self, index = None):
  item = self[index]
  screen_name=None
  try:
   screen_name = self.get_screen_name(index)
   twitter_id = self[index]['id']
  except:
   pass
  item_type = self.get_item_type(index)
  if self.session.config['UI']['confirmRemovePost']:
   if self.session.is_current_user(screen_name) or item_type == "DM":
    confirmation = question_dialog(caption=_("Remove Tweet"), message=_("The post you are trying to remove will also be deleted from Twitter.  Do you still wish to remove it?"))
    if confirmation != wx.ID_YES:
     return output.speak(_("Canceled."), True)
  if self.session.is_current_user(screen_name) or item_type == "DM":
   try:
    if item_type == "DM":
     self.session.api_call("destroy_direct_message", preexec_message=_("Deleting direct message"), action=_("deleting direct message"), id=twitter_id)
    else:
     self.session.api_call("destroy_status", preexec_message=_("removing item"), action=_("removing item"), id=twitter_id)
   except TweepError as e:
    if e.response is None or e.response.status != 404:
     raise
  super(Twitter, self).remove_item(index)

 def add_item_by_time (self, item):
  super(Twitter, self).extend([item])

 @buffer_defaults
 def get_all_screen_names (self, index=None):
  who = []
  try:
   who.append(self.get_screen_name(index))
   who.extend(self.get_mentions(index))
  except:
   pass
  if not who:
   who = [""]
  return misc.RemoveDuplicates(who)

 @buffer_defaults
 def item_timestamp (self, item=None):
  return self.standardize_timestamp(item.get('created_at', None))

 @buffer_defaults
 def get_item_type(self, index=None):
  item = self[index]
  if 'source' not in item:
   return "DM"
  else:
   return _("tweet")

 def handles_post(self, post):
  #Returns a bool indicating if this buffer handles the provided post.
  return False

 def handle_pushed_item(self, item):
  self.handle_update([item])

 @buffer_defaults
 def find_audio_handler(self, index=None, item=None):
  url = super(Twitter, self).find_audio_handler(index=index, item=item)
  if url is None:
   urls = super(Audio, self).get_urls(index=index, item=item)
   if "#audio" in self.get_hash_tags(index, item) and len(urls) > 0:
    url = urls[0]
  return url

 def extend(self, items, *args, **kwargs):
  super(Twitter, self).extend(self.process_users(items), *args, **kwargs)

 