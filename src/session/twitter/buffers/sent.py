from logger import logger
logging = logger.getChild('sessions.twitter.buffers.sent')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import calendar
import rfc822
from conditional_template import ConditionalTemplate as Template
import output
import threading

from tweets import Tweets
from main import Twitter
from core.sessions.buffers.update_type import set_update_type
from core.sessions.buffers import field_metadata as meta

class Sent (Tweets):
 def sort_key(self, item):
  return self.standardize_timestamp(item["created_at"])

 def __init__ (self, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.item_name = _("sent item")
  self.item_name_plural = _("sent items")
  super(Sent, self).__init__ (*args, **kwargs)
  if 'spoken' not in self.buffer_metadata or self.buffer_metadata['spoken'] == self.session.config['templates']['default_template']:
   self.buffer_metadata['spoken'] = '$if(geo){*geo* } about $when, $if(dm){DM to $rcpt_name: }$message'
  if 'clipboard' not in self.buffer_metadata.keys():
   self.buffer_metadata['clipboard'] = self.buffer_metadata['spoken']
  self.set_field('dm', _("Direct Message"), (lambda item: bool('recipient' in item and item['recipient'])), field_type=meta.FT_BOOL)
  self.set_field('rcpt_name', _("DM Recipient's Name"), (lambda item: item.get('recipient', {}).get('name', None)), filter=True)
  self.set_field('rcpt_screen_name', _("DM Recipient's Screen Name"), (lambda item: item.get('recipient', {}).get('screen_name', None)), filter=True)
  self.init_done_event.set()

 def retrieve_update(self, *args, **kwargs):
  tweets = self.timeline_update(update_function_name='get_user_timeline', since_id=self.get_max_sent_item_id(), include_rts=True, include_entities=True)
  tweets.extend(self.retrieve_new_sent_directs())
  return tweets

 def retrieve_new_sent_directs (self):
  return self.timeline_update(update_function_name='get_sent_messages', since_id=self.get_max_sent_direct_id(), include_entities=True, full_text=True)

 def process_update(self, update, *args, **kwargs):
  update = Tweets.process_update(self, update)
  update.sort(key=lambda a: calendar.timegm(rfc822.parsedate(a['created_at'])))
  return update

 def item_exists(self, item):
  return self.storage.find_one(dict(id=item['id']))

 def get_max_sent_item_id (self):
  id = 1
  for i in range(len(self) - 1, -1, -1):
   if 'source' in self[i] and 'id' in self[i]:
    id = self[i]['id']
    break
  return id

 def get_max_sent_direct_id(self):
  id = 1
  for i in range(len(self) - 1, -1, -1):
   if 'source' not in self[i] and 'id' in self[i]:
    id = self[i]['id']
    break
  return id

 @buffer_defaults
 def get_mentions (self, index=None):
  who = super(Sent, self).get_mentions(index)
  if self[index].has_key('recipient') and self[index]['recipient'].has_key('screen_name'):
   who.append(self[index]['recipient']['screen_name'])
  return who

 def handles_post(self, post):
  if 'direct_message' in post and post['direct_message']['sender']['screen_name'].lower() == self.session.username.lower():
   return True
  if 'user' in post and post['user']['screen_name'].lower() == self.session.username.lower():
   return True

 def handle_pushed_item(self, item):
  if 'direct_message' in item:
   self.handle_update([item['direct_message']])
  else:
   self.handle_update([item])
