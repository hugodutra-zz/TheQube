from logger import logger
logging = logger.getChild('core.sessions.buffers.main')

from copy import deepcopy
from pydispatch import dispatcher

import core
import output
import signals
from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.sound.sound import Sound
from core.sessions.undo import Undo
import sessions

class Buffers (Sound, Undo):

 def __init__ (self, *args, **kwargs):
  self.buffers = []
  self.nav_buffers = []
  super(Buffers, self).__init__(*args, **kwargs)
  if 'buffers' not in self.config.keys():
   self.config['buffers'] = {}
  self.buffer_metadata = self.config['buffers']
  if 'init_order' not in self.buffer_metadata:
   self.buffer_metadata['init_order'] = []
  self.init_order = self.buffer_metadata['init_order']
  if 'nav_order' not in self.buffer_metadata:
   self.buffer_metadata['nav_order'] = []
  self.nav_order = self.buffer_metadata['nav_order']
  self.save_config()
 
 def remove_buffer_ordering(self, location=None, buf_index=None):
  if location in self.init_order:
   self.init_order.remove(location)
  if buf_index is not None:
   if buf_index in self.nav_order:
    self.nav_order.remove(buf_index)
   for i in range(len(self.nav_order)):
    if self.nav_order[i] > buf_index:
     self.nav_order[i] -= 1
   self.update_navigation_buffers()

 def add_buffer (self, buffer):
  #Adds the provided buffer to this session.
  logging.debug("Adding buffer %s to session %s" % (buffer, self))
  self.buffers.append(buffer)
  if hasattr(buffer, 'location') and buffer.location in self.buffer_metadata and buffer.location not in self.init_order:
   self.init_order.append(buffer.location)
  buf_index = len(self.buffers) - 1
  if buf_index not in self.nav_order:
   self.nav_order.append(buf_index)
  self.update_navigation_buffers()
  if 'replaces_spec' in buffer.buffer_metadata:
   replaced = self.find_buffer_from_spec(buffer.buffer_metadata['replaces_spec'])
   self.swap_buffers(replaced, buffer)
   self.replace_buffer(replaced, buffer)
  self.save_config()
  return buf_index

 def remove_buffer(self, buffer, announce=True):
  """Removes the provided buffer from this session"""
  logging.debug("Removing buffer %s from session %s" % (buffer.name, self.name))
  if buffer.replaces is not None:
   self.replace_buffer(None, buffer)
  key = None
  if hasattr(buffer, 'location'):
   key = buffer.location
  buf_index = self.get_buffer_index(buffer)
  buffer.shutdown()
  self.buffers.remove(buffer)
  self.remove_buffer_ordering(location=key, buf_index=buf_index)
  prev_buffer = None
  while prev_buffer is None:
   try:
    (prev_buffer_name, i, j) = self.pop()
   except:
    if hasattr(self, '_default_buffer'):
     prev_buffer_name = self._default_buffer.name
    elif len(self.nav_buffers):
     prev_buffer_name = self.nav_buffers[-1].name
    else:
     break
   if prev_buffer_name == buffer.name:
    continue
   prev_buffer = self.get_buffer_by_name(prev_buffer_name)
   if prev_buffer not in self.nav_buffers:
    prev_buffer = None
  if self.nav_buffers:
   self.set_buffer(self.get_navigation_index(prev_buffer), False)
   if announce:
    self.announce_buffer()
  else:
   self.current_buffer = None
   output.speak(_("No buffers remaining."), True)
  self.save_config()

 def update_navigation_buffers(self):
  self.nav_buffers = []
  for i in self.nav_order:
   if i < len(self.buffers):
    self.nav_buffers.append(self.buffers[i])
   else:
    self.nav_buffers.append(None)
 
 def register_buffer (self, name, type, set_focus=True, announce=True, prelaunch_message="", postlaunch_message="", prevent_duplicates=True, *args, **kwargs):
  """Registers buffer  in session buffer list."""
  logging.debug("%s: Registering %s" % (self, name))
  if self.get_buffer_by_name(name) != None and prevent_duplicates:
   logging.debug("Buffer %s already exists." % name)
   num = self.get_buffer_index(self.get_buffer_by_name(name))
   if set_focus:
    self.set_buffer(self.get_navigation_index(buf_index=num))
   if announce:
    self.announce_buffer(interrupt=False)
   return num
  prelaunch_message and output.speak(prelaunch_message, True)
  try:
   new = type(name=name, session=self, *args, **kwargs)
  except:
   logging.exception("Unable to initialize an instance of buffer.%s " % type)
   return None
  if self.buffer_exists(new):
   logging.warning("%s: Prevented duplicate buffer registration of buffer %s." % (self.name, name))
   return None
  if new is None: #Something strange is going on.
   logging.debug("Attempted new buffer creation but got back a None object.  Aborting.")
   return None
  dispatcher.send(sender=self, signal=signals.buffer_created, buffer=new)
  num = self.add_buffer(new)
  if set_focus and num in self.nav_order:
   self.set_buffer(self.get_navigation_index(buf_index=num))
  postlaunch_message and output.speak(postlaunch_message, True)
  if announce:
   self.announce_buffer(interrupt=False)
  return num

 def buffer_exists(self, buffer):
  #Returns True/False if buffer is currently registered in this session's buffers list."""
  return buffer in self.buffers
 
 def normalize_nav_index(self, nav_index):
  if len(self.nav_order) == 0:
   nav_index = -1
  else:
   if nav_index < 0:
    nav_index = len(self.nav_order)-1
   elif nav_index >= len(self.nav_order):
    nav_index = 0
  return nav_index
 
 def set_buffer (self, nav_index, undoable=True):
  if len(self.nav_order) < 2: #We wouldn't be able to undo this action anyway.
   undoable = False
  nav_index = self.normalize_nav_index(nav_index)
  if undoable and nav_index != self.get_navigation_index():
   self.push((self.current_buffer.name, self.current_buffer.index, -1))
  if nav_index < 0:
   del self.buffer_metadata['current']
  else:
   self.buffer_metadata['current'] = nav_index
  self.save_config()
  dispatcher.send(sender=self, signal=signals.change_current_buffer, buffer = self.current_buffer)
  return nav_index

 def set_buffer_and_index(self, nav_index, index, undoable=True, announce=True):
  if len(self.nav_order) < 2: #We wouldn't be able to undo this action anyway.
   undoable = False
  nav_index = self.normalize_nav_index(nav_index)
  if undoable and (nav_index != self.get_navigation_index() or index != self.current_buffer.index):
   self.push((self.current_buffer.name, self.current_buffer.index, self.buffers[self.get_buffer_index(nav_index=nav_index)].index))
  self.set_buffer(nav_index, False)
  if self.current_buffer is not None:
   self.current_buffer.set_index(index,False)
   if announce:
    self.current_buffer.speak_item(honor_mute=False)
    self.announce_buffer(interrupt=False)
  return nav_index

 def get_buffer_by_name(self, name):
  for item in self.buffers:
   if item.name.lower() == name.lower():
    return item

 @buffer_defaults
 def get_buffer_index(self, buffer=None, nav_index=None):
  if nav_index is None:
   return self.buffers.index(buffer)
  else:
   return self.nav_order[nav_index]

 @buffer_defaults
 def get_navigation_index(self, buffer=None, buf_index=None):
  if buf_index is None:
   buf_index = self.get_buffer_index(buffer)
  return self.nav_order.index(buf_index)
 
 def shutdown(self, *args, **kwargs):
  logging.debug("Shutting down all buffers in session %s" % self.name)
  for buffer in self.buffers:
   buffer.shutdown(end=True)
   dispatcher.send(sender=self, signal=signals.buffer_destroyed, buffer=buffer)
  super(Buffers, self).shutdown(*args, **kwargs)

 def get_current_buffer(self):
  if len(self.nav_order) == 0:
   return None
  nav_index = self.buffer_metadata.get('current', -1)
  if nav_index < 0 or nav_index >= len(self.nav_order):
   nav_index = self.normalize_nav_index(nav_index)
   self.set_buffer(nav_index, False)
  return self.nav_buffers[nav_index]

 def set_current_buffer(self, buffer):
  if buffer is not None:
   nav_index = self.get_navigation_index(buffer)
  else:
   nav_index = -1
  self.set_buffer(nav_index, False)

 current_buffer = property(fget = get_current_buffer, fset = set_current_buffer)

 def activate(self, *args, **kwargs):
  if self.buffers:
   try:
    self.announce_buffer(interrupt=False)
   except:
    pass
  super(Buffers, self).activate(*args, **kwargs)

 def finish_initialization (self, *args, **kwargs):
  try:
   logging.debug("%s: Buffers post initialization: registering stored buffers." % self.name)
   self.register_stored_buffers()
   logging.debug("%s: Buffers post initialization: registering default buffers." % self.name)
   self.register_default_buffers()
   logging.debug("%s: Removing rogue navigation indexes." % self.name)
   rogue_indexes = [i for i in self.nav_order if i >= len(self.buffers)]
   for i in rogue_indexes:
    self.nav_order.remove(i)
   self.update_navigation_buffers()
   if 'current' not in self.buffer_metadata and len(self.nav_buffers) > 0:
    self.set_buffer(0, False)
   if sessions.current_session == self:
    self.announce_buffer()
  except:
   logging.exception("%s: Unable to register buffers." % self.name)
  super(Buffers, self).finish_initialization(*args, **kwargs)

 def register_default_buffers(self):
  pass
 
 def register_stored_buffers(self):
  import session
  buffers = []
  for buf in self.init_order:
   buffers.append(buf)
  for buf in self.buffer_metadata.keys():
   if buf not in buffers and hasattr(self.buffer_metadata[buf], 'has_key') and self.buffer_metadata[buf].has_key('visible') and self.buffer_metadata[buf]['visible']:
    buffers.append(buf)
  for buf_key in buffers:
   try:
    buf = self.buffer_metadata[buf_key]
    type = getattr(eval(buf['class_module']), buf['class_name'])
    args = list(buf['args'])
    kwargs = deepcopy(buf['kwargs'])
    name = kwargs['name']
    del kwargs['name']
    if self.register_buffer(name, type, False, announce=False, *args, **kwargs) is None:
     self.remove_buffer_ordering(location=buf_key, buf_index=len(self.buffers))
   except:
    self.remove_buffer_ordering(location=buf_key, buf_index=len(self.buffers))
    logging.exception("Unable to register buffer")

 def move_buffer (self, buffer, step):
  nav_index = self.get_navigation_index(buffer)
  buf_index = self.get_buffer_index(nav_index=nav_index)
  new = nav_index + step
  if new >= len(self.nav_order):
   new += 1
   new %= len(self.nav_order)
  elif new < 0:
   new -= 1
   new = len(self.nav_order) - (abs(new) % len(self.nav_order))
  self.nav_order.remove(buf_index)
  self.nav_order.insert(new, buf_index)
  self.update_navigation_buffers()
  self.set_buffer(new, False)
  self.save_config()

 def replace_buffer(self, buffer, replacement, set_focus=True, announce=True):
  if self.current_buffer is replacement:
   #Follow the replacement if it's the current buffer.
   set_focus = True
  if buffer is None:
   replaced = replacement.replaces
   self.nav_order.insert(self.get_navigation_index(replacement), self.get_buffer_index(replaced))
   replacement.replaces = None
   del replacement.buffer_metadata['replaces_spec']
  else:
   replacement.replaces = buffer
   replacement.buffer_metadata['replaces_spec'] = self.buffer_spec(buffer)
   del self.nav_order[self.get_navigation_index(replacement)]
   self.nav_order[self.get_navigation_index(buffer)] = self.get_buffer_index(replacement)
  self.save_config()
  self.update_navigation_buffers()
  if set_focus:
   self.set_buffer(self.get_navigation_index(replacement), False)
  if announce:
   self.announce_buffer(interrupt=False)

 @buffer_defaults
 def announce_buffer(self, buffer=None, interrupt=True):
  if buffer == None:
   answer = _("No current buffer.")
  else:
   answer = _(buffer.display_name)
   if not buffer:
    answer = _("%s: Empty.") % answer
   else:
    answer = _("%s: %d of %d items.") % (answer, len(buffer)-buffer.index, len(buffer))
  output.speak(answer, interrupt)

 def buffer_spec(self, buffer):
  return (buffer.__class__.__name__, buffer.name)

 def find_buffer_from_spec(self, spec):
  cls, name = spec
  for i in self.buffers:
   if i.__class__.__name__ == cls and i.name == name:
    return i

 def swap_buffers(self, buffer1, buffer2):
  nav_index1 = self.get_navigation_index(buffer1)
  nav_index2 = self.get_navigation_index(buffer2)
  self.nav_order[nav_index1], self.nav_order[nav_index2] = self.nav_order[nav_index2], self.nav_order[nav_index1]
  self.update_navigation_buffers()
  self.save_config()

 def navigate_to_item_matching(self, search_key, search):
  #Always check the current buffer first.
  buffers = list(self.nav_buffers)
  buffers.remove(self.current_buffer)
  buffers.insert(0, self.current_buffer)
  for i in buffers:
   try:
    index = i.get_index_matching(search_key, search)
    return self.set_buffer_and_index(self.get_navigation_index(i), index)
   except Exception as e:
    if not isinstance(e, (ValueError, KeyError)):
     raise
    continue
  self.play(self.config['sounds']['boundary'])
  self.current_buffer.speak_item()
