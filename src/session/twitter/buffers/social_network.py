from logger import logger
logging = logger.getChild('sessions.twitter.buffers.social_network')

import output
import threading

from users import Users
from core.sessions.buffers.update_type import set_update_type

class SocialNetwork (Users):

 def __init__ (self, method, session=None, *args, **kwargs):
  self.init_done_event = threading.Event()
  self.initial_update = True
  followers_buffer = None
  friends_buffer = None
  for i in session.buffers:
   if hasattr(i, 'is_followers_buffer') and i.is_followers_buffer:
    followers_buffer = i
   if hasattr(i, 'is_friends_buffer') and i.is_friends_buffer:
    friends_buffer = i
   if followers_buffer and friends_buffer:
    break
  if not (followers_buffer and friends_buffer):
   logging.debug("No followers or friends buffer found, cannot launch social network buffer.")
   return
  self.method = method
  self.followers = followers_buffer
  self.friends = friends_buffer
  self.item_type = _("user")
  self.item_type_plural = _("users")
  super(SocialNetwork, self).__init__ (session=session, *args, **kwargs)
  self.set_flag('configurable', False)
  self.set_flag('exportable', False)
  self.init_done_event.set()

 @set_update_type
 def retrieve_update(self, update_type=None, *args, **kwargs):
  if update_type != self._update_types['initial']:
   return
  master = dict()
  followers_ids = []
  for f in self.followers:
   followers_ids.append(f['id'])
   if f['id'] not in master:
    master[f['id']] = f
  friends_ids = []
  for f in self.friends:
   friends_ids.append(f['id'])
   if f['id'] not in master:
    master[f['id']] = f
  if self.method == 'intersection':
   result_ids = filter(lambda x: x in friends_ids, followers_ids)
  elif self.method == 'friend_but_not_follower':
   result_ids = filter(lambda x: x not in followers_ids, friends_ids)
  else:
   self.method = 'follower_but_not_friend'
   result_ids = filter(lambda x: x not in friends_ids, followers_ids)
  network = []
  for id in result_ids:
   network.append(master[id])
  network.reverse()
  return network

 @set_update_type
 def report_update(self, items, update_type=None, *args, **kwargs):
  if len(items) == 1:
   msg = "Social network contains %d user." % len(items)
  else:
   msg = "Social network contains %d users." % len(items)
  super(SocialNetwork, self).report_update(items, msg=msg, update_type=update_type)
