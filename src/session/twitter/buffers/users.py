from logger import logger
logging = logger.getChild('sessions.twitter.buffers.users')

import core.sessions.buffers.field_metadata as meta
from core.sessions.buffers.buffer_defaults import buffer_defaults
from core.sessions.buffers.update_type import set_update_type
from core.sessions.buffers.buffers import Buffer

from main import Twitter
from core.sessions.buffers.buffers import Dismissable

class Users (Dismissable, Twitter):
 rapid_access = ['id']

 def __init__ (self, username=None, *args, **kwargs):
  if not username:
   username = kwargs['session'].username
   kwargs['count'] = 200
   kwargs['maxAPIPerUpdate'] = 15
  self.username = username
  super(Users, self).__init__(*args, **kwargs)
  self.default_template = 'default_followers_friends'
  self.store_args({'username':username})
  self.buffer_metadata['interval'] = self.session.config['updates']['friendsInterval']
  self.set_flag('updatable', False)
  self.set_flag('temp', True)
  self.set_field('name', _("Name"), None)
  self.set_field('screen_name', _("Screen name"), None)
  self.set_field('location', _("Location"), None)
  self.set_field('bio', _("Description"), 'description')
  self.set_field('protected', _("Protected"), None, field_type=meta.FT_BOOL, filter=False)
  self.set_field('followers_count', _("Follower count"), None, field_type=meta.FT_NUMERIC)
  self.set_field('friends_count', _("Friend count"), None, field_type=meta.FT_NUMERIC)
  self.set_field('tweets_count', _("Number of tweets"), 'statuses_count', field_type=meta.FT_NUMERIC)
  self.set_field('notifications', _("Device notifications"), None, field_type=meta.FT_BOOL, filter=False)
  self.set_field('local_time', _("User's local time"), ('utc_offset', self.user_local_time), filter=False)
  self.set_field('local_date', _("User's local date",), ('utc_offset', self.user_local_date), filter=False)
  self.set_field('last_tweet_time', _("Last Tweet Time"), (('status', 'created_at'), self.standardize_timestamp, self.actual_time), filter=False)
  self.set_field('last_tweet_date', _("Last Tweet Date"), (('status', 'created_at'), self.standardize_timestamp, self.actual_date), filter=False)
  self.set_field('last_tweet_when', _("Last Tweet Relative Time"), (('status', 'created_at'), self.standardize_timestamp, self.relative_time), filter=False)

 @buffer_defaults
 def get_message(self, index=None):
  return self.RetrievePost(index)[-1]

 @buffer_defaults
 def remove_item (self, index=None):
  self.session.interface.Unfollow()
  Buffer.remove_item(self, index=index, announce=False)

 def process_users(self, items):
  return items

 def get_next_item_time_step_index (self, step, index=0):
  raise AttributeError

 def get_prev_item_time_step_index (self, step, index=0):
  raise AttributeError

 def get_mentions (self, index=None):
  return []

 def process_update(self, update, *args, **kwargs):
  update.reverse()
  return update

 def extend(self, items, *args, **kwargs):
  index = self.index
  self.clear()
  super(Users, self).extend(items)
  self.index = index

 @set_update_type
 def report_update(self, items, msg="", update_type=None, *args, **kwargs):
  if not msg:
   if self.session.is_current_user(self.username):
    msg = _("%s updated") % self.item_name_plural
   else:
    msg = _("%s for %s updated") % (self.item_name_plural, self.username)
  super(Users, self).report_update(items, msg=msg, update_type=update_type)

