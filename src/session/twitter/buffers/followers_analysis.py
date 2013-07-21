from logger import logger
logging = logger.getChild('sessions.twitter.buffers.follower_analysis')

from core.sessions.buffers.buffer_defaults import buffer_defaults
import copy
import output
import threading

from users import Users
from core.sessions.buffers.update_type import set_update_type
from core.sessions.buffers import field_metadata as meta

class FollowersAnalysis (Users):

 def __init__ (self, session=None, *args, **kwargs):
  self.init_done_event = threading.Event()
  followers_buffer = None
  for i in session.buffers:
   if hasattr(i, 'is_followers_buffer') and i.is_followers_buffer:
    followers_buffer = i
    break
  if not followers_buffer:
   logging.debug("No followers buffer found, cannot launch followers analysis buffer.")
   return
  self.old_followers_location = '_OldFollowers'
  self.cur_followers_location = followers_buffer.location
  if self.old_followers_location not in session.storage.keys():
   with session.storage_lock: session.storage[self.old_followers_location] = []
  super(FollowersAnalysis, self).__init__ (session=session, *args, **kwargs)
  self.set_flag('configurable', False)
  self.set_flag('exportable', False)
  self.set_field('new_follower', _("New Follower"), '_new_follower', field_type=meta.FT_BOOL, filter=False)
  self.init_done_event.set()

 @set_update_type
 def retrieve_update(self, update_type=None, *args, **kwargs):
  if update_type != self._update_types['initial']:
   return
  with self.session.storage_lock:
   old_followers = self.session.storage[self.old_followers_location]
   cur_followers = copy.deepcopy(self.session.storage[self.cur_followers_location])
   self.session.storage[self.old_followers_location] = copy.deepcopy(cur_followers)
  analysis = []
  logging.debug("Analyzing %s current followers against %s old followers." % (len(cur_followers), len(old_followers)))
  for i in range(len(cur_followers) - 1, -1, -1):
   cur_followers[i]['_new_follower'] = True
   for j in range(len(old_followers) - 1, -1, -1):
    old_followers[j]['_new_follower'] = False
    if cur_followers[i]['id'] == old_followers[j]['id']:
     del cur_followers[i]
     del old_followers[j]
     break
  self.len_cur_followers = len(cur_followers)
  self.len_old_followers = len(old_followers)
  analysis.extend(old_followers)
  analysis.extend(cur_followers)
  analysis.reverse()
  return analysis

 @set_update_type
 def report_update(self, items, update_type=None, *args, **kwargs):
  if self.len_cur_followers == 1:
   msg = "%d new follower" % self.len_cur_followers
  else:
   msg = "%d new followers" % self.len_cur_followers
  if self.len_old_followers == 1:
   msg = "%s, %d deserter" % (msg, self.len_old_followers)
  else:
   msg = "%s, %d deserters" % (msg, self.len_old_followers)
  super(FollowersAnalysis, self).report_update(items, msg=msg, update_type=update_type)

 @buffer_defaults
 def get_template(self, name="spoken"):
  return "$if(new_follower){New follower }{Deserter }" + super(FollowersAnalysis, self).get_template(name)
