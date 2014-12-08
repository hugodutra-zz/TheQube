# -*- coding: utf-8 -*-

from logger import logger
logging = logger.getChild('core.buffers.updating')

from pydispatch import dispatcher

import config
import output
import sessions
import signals
import threading
from utils.repeating_timer import RepeatingTimer
from utils.thread_utils import call_threaded

from core.sessions.buffers.buffers.buffer import Buffer
from core.sessions.buffers.update_type import set_update_type

class Updating (Buffer):

 def __init__ (self, session, interval=None, *args, **kwargs):
  self._update_types = dict(initial=1, auto=2, forced=3, default=2)
  super(Updating, self).__init__(session, *args, **kwargs)
  self.update_lock = threading.Lock()
  self.set_flag('updatable', True)
  if not interval and interval != 0:
   try:
    interval = self.buffer_metadata['interval']
   except:
    interval = session.config.get('updates', {}).get('checkInterval', 0)
  self.buffer_metadata['interval'] = interval
  self.interval = self.buffer_metadata['interval']
  if not hasattr(self, 'item_name'):
   self.item_name = _("message")
   self.item_name_plural = _("messages")
  self.item_sound = ""
  if hasattr(self.session, 'default_sound'):
   self.item_sound = self.session.default_sound
  if self.interval:
   self.setup_timer()

 def shutdown(self, *args, **kwargs):
  self.deactivate_timer()
  super(Updating, self).shutdown(*args, **kwargs)

 def deactivate_timer(self):
  if self.buffer_metadata['interval']:
   try:
    self.timer.stop()
    logging.debug("%s: Deactivated update timer in buffer %s" % (self.session, self))
   except:
    logging.exception("%s: Error shutting down update timer in session %s." % (self.session, self))

 def set_new_interval (self, interval=None):
  if interval == None:
   interval = self.buffer_metadata['interval']
  if self.buffer_metadata['interval']:
   self.deactivate_timer()
  self.buffer_metadata['interval'] = interval
  if interval:
   self.setup_timer(run_immediately=False)

 def setup_timer (self, run_immediately=True):
  if self.buffer_metadata['interval']:
   self.timer = RepeatingTimer(self.buffer_metadata['interval'], self.update)
   self.timer.start()
   if run_immediately:
    logging.info("%s: performing immediate update in buffer %s" % (self.session, self))
    call_threaded(self.update, update_type=self._update_types['initial'])

 @set_update_type
 def update(self, update_type=None, *args, **kwargs):
  """The Update method.  Called to check for new  information and consolidate it into this buffer."""
  if hasattr(self, 'init_done_event'):
   self.init_done_event.wait()
  if not self.get_flag('updatable') and update_type == self._update_types['forced']:
   raise UpdateError("Buffer %r is not updatable." % self)
  if not self.update_lock.acquire(False):
   if update_type == self._update_types['forced']:
    output.speak(_("Update already in progress; please wait."), True)
   return
  try:
   if update_type == self._update_types['forced']:
    output.speak(self.update_message, True)
   logging.debug("Synchronizer: Updating buffer %s." % self)
   try:
    new = self.retrieve_update(update_type=update_type)
   except:
    return logging.exception("%s: Error during update process in buffer %s" % (self.session, self))
   self.handle_update(new, update_type=update_type, *args, **kwargs)
  finally:
   self.update_lock.release()

 @set_update_type
 def handle_update(self, data, update_type=None, *args, **kwargs):
  data = self.process_update(data, update_type=update_type)
  if data and self.session.buffer_exists(self):
   #Add new items to buffer storage
   try:
    self.extend(items=data, update_type=update_type, *args, **kwargs)
   except:
    return logging.exception("%s: Error writeing new items to storage in buffer %s." % (self.session, self))
   #Send an event out with the new items we got for any buffers that depend on this buffer's data.
   try:
    dispatcher.send(sender=self, signal=signals.buffer_updated, items=data, update_type=update_type, **kwargs)
   except:
    logging.exception("%s: Error sending buffer_updated event in buffer %s." % (self.session, self))
  self.report_update(data, update_type=update_type)

 def retrieve_update(self, *args, **kwargs):
  #Dumby method.  Replace with code to update this buffer.
  raise NotImplementedError

 def process_update(self, update, *args, **kwargs):
  return self.find_new_data(update)

 @set_update_type
 def report_update(self, items, msg="", update_type=None, *args, **kwargs):
  if not msg:
   use_default_msg = True
  else:
   use_default_msg = False
  counter = len(items)
  if not counter:
   if update_type == self._update_types['forced']:
    self.speak(_("No new %s.") % self.item_name_plural, honor_mute=False)
   return
  try:
   self.play(self.item_sound)
  except:
   pass
  if sessions.current_session is not self.session:
   msg = _("%s: %s") % (self.session, msg)
  if use_default_msg:
   if counter == 1:
    item_name = _(self.item_name)
   else:
    item_name = _(self.item_name_plural)
   msg = ngettext("%(msg)s1 %(item_name)s.", "%(msg)s%(num)d %(item_name)s.", counter) % {'msg': msg, 'item_name': item_name, 'num': counter}
  if update_type != self._update_types['auto']:
   self.speak(_(msg), honor_mute=False)
  else:
   self.speak(_(msg))

 def extend(self, items=[], *args, **kwargs):
  super(Updating, self).extend(items)

 @property
 def update_message(self):
  return _("Checking for %s.") % self.item_name_plural


class UpdateError(Exception): pass
