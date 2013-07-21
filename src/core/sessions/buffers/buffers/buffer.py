from logger import logger
logging = logger.getChild('core.sessions.buffers.buffers.buffer')

from core.sessions.buffers.buffer_defaults import buffer_defaults
from pydispatch import dispatcher
import output
import signals
from conditional_template import ConditionalTemplate as Template
from utils.thread_utils import call_threaded
from core.sessions.buffers import field_metadata as meta

from core.named_object import NamedObject

class Buffer(NamedObject):
 """The parent buffer class.  """


 replaces = None #Is this buffer currently replacing another buffer?
 dead = False #Is the buffer dead?

 def __init__ (self, session=None, mute=None, replaces=None, replaces_spec=None, data=[], *args, **kwargs):
  super(Buffer, self).__init__(*args, **kwargs)
  self.session = session
  if replaces is not None:
   replaces_spec = self.session.buffer_spec(replaces)
  try:
   if not  hasattr(self, "buffer_metadata"):
    self.buffer_metadata = dict()
   if 'sounds' not in self.buffer_metadata:
    self.buffer_metadata['sounds'] = dict()
   if 'mute' not in self.buffer_metadata['sounds']:
    if mute == None:
     self.buffer_metadata['sounds']['mute'] = self.session.config['sounds']['defaultBufferMute']
    else:
     self.buffer_metadata['sounds']['mute'] = mute
   if 'flags' not in self.buffer_metadata:
    self.buffer_metadata['flags'] = dict()
   self.buffer_metadata['class_module'] = self.__class__.__module__
   self.buffer_metadata['class_name'] = self.__class__.__name__
   self.buffer_metadata['visible'] = True
   if replaces_spec is not None:
    self.buffer_metadata['replaces_spec'] = replaces_spec
   if not  hasattr(self, "storage"):
    self.storage = list()
   if not hasattr(self, "index"):
    self._index = self.index = 0
    self.set_index(0)
   if not hasattr(self, "initial_update"):
    self.initial_update = False
   if not hasattr(self, "item_fields"):
    self.item_fields = dict()
   self.set_field('total', _("Total"), (lambda index: len(self)), field_type=meta.FT_NUMERIC, filter=False)
   self.set_field('index', _("Index"), (lambda index: len(self) - index), field_type=meta.FT_NUMERIC, filter=False)
  except:
   return logging.exception("%s: Error building buffer %s" % (self.session, self.name))
  self.store_args({'data': data}, *args, **kwargs)
  self.__has_looped__ = 0
  self.set_flag('configurable', True)
  self.set_flag('clearable', True)
  self.set_flag('temp', True)
  self.set_flag('fixed_template', False)
  self.active = True

 def find_new_data(self, items):
  """Return any items from the given sequence that aren't in this buffer."""
  return self.items_exist(items)[0]

 def clear(self):
  if not self.get_flag('clearable'):
   return logging.warn("%s: Attempted clearing of unclearable buffer %s" % (self.session, self))
  logging.debug("Clearing buffer %s" % self)
  if len(self) > 0:
   self.set_index(0)
   self.do_clear()

 def do_clear(self):
  del(self.storage[:])
  dispatcher.send(sender=self, signal=signals.clear_buffer, buffer=self.name)

 def remove_item_from_storage(self, index):
  del(self.storage[index])

 @buffer_defaults
 def remove_item(self, index=None, announce=True):
  item = self[index]
  self.remove_item_from_storage(index)
  dispatcher.send(sender=self, signal=signals.remove_item, item=item)
  del(item)
  if self.index  == len(self):
   self.set_index(self.index-1, False)
  if announce:
   output.speak(_("Item deleted."), True)

 def shutdown(self, end=False):
  if self.dead:
   logging.debug("The {0} buffer is dead, shutdown has already been done.".format(self.name))
   return
  logging.debug("%s: Shutting down buffer %s.  End: %r." % (self.session, self, end))
  if not end:
   self.buffer_metadata['visible'] = False
   dispatcher.send(sender=self, signal=signals.dismiss_buffer, buffer=self)
   if self.get_flag('temp'):
    self.destroy()
  self.dead = True

 def destroy(self):
  call_threaded(self.do_destroy)

 def do_destroy(self):
  logging.debug("%s: Destroying buffer %s" % (self.session, self))
  self.clear()
  del self.buffer_metadata

 def extend(self, items, *args, **kwargs):
   self.storage.extend(items)

 def __contains__(self, item):
  return item in self.storage
 item_exists = __contains__

 def items_exist(self, items):
  """Given a sequence of items, returns two sequences, the first containing the items which do not exist in the current buffer, the second with those which do."""
  new = []
  existing = []
  working = items
  for i in items:
   if i in self:
    existing.append(i)
    new.remove(i)
    working.remove(i)  
  new = working
  return (new, existing)

 def compare_items(self, item1, item2):
  """Returns a bool indicating if the two items are the same"""
  return item1 == item2


 def get_max_index(self):
  return len(self) - 1

 def get_index (self):
  if self._index > len(self) - 1:
   index = len(self) - 1
  elif self._index < 0:
   index = 0
  else:
   index = self._index
  return index

 def set_index (self, index, undoable=True):
  current_index = self.get_index()
  if index > len(self) - 1:
   index = len(self) - 1
  elif index < 0:
   index = 0
  if undoable and index != current_index:
   self.session.push((self.name, current_index, -1))
  self._index = index

 index = property(get_index, set_index)

 def next_item(self):
  #By default returns the next item in buffer until last, where upon it keeps returning the last.
  self.index += 1
  return self[self.index]

 def prev_item (self):
  #By default returns the previous item in buffer until first, where upon it keeps returning the first.
  self.index -= 1
  return self[self.index]

 def __iter__ (self):
  return iter(self.storage)

 # This method name must deviate from its counterpart in the standard list
 # type, to avoid a conflict with the Buffer.index property.
 def index_of(self, item):
  return self.storage.index(item)

 def __list__(self):
  return list(self.storage)

 def __len__(self):
  return len(self.storage)

 def __getitem__(self, val):
  return self.storage[val]

 def insert(self, index, item):
  self.storage.insert(index, item) # TODO: fix for MongoDB

 def __str__(self):
  return _("buffer %s") % self.name

 def store_args(self, _dict={}, *args, **kwargs):
  if 'session' in kwargs:
   del kwargs['session']
  kwargs.update(_dict)
  if 'args' not in self.buffer_metadata:
   self.buffer_metadata['args'] = []
  if 'kwargs' not in self.buffer_metadata:
   self.buffer_metadata['kwargs'] = {}
  self.buffer_metadata['args'] = list(set(list(args) + list(self.buffer_metadata['args'])))
  self.buffer_metadata['kwargs'].update(kwargs)

 def get_flag (self, flag):
  return self.buffer_metadata['flags'].get(flag, False)

 def set_flag (self, flag, val):
  assert val in (True, False)
  self.buffer_metadata['flags'][flag] = val

 @buffer_defaults
 def format_item(self, index=None, item=None, template="spoken"):
  template = Template(self.get_template(template))
  mapping = self.get_item_data(index=index, item=item)
  return template.Substitute(mapping)

 @buffer_defaults
 def format_item_clipboard(self, index=None):
  return self.format_item(index, template="clipboard")

 def toggle_buffer_mute (self):
  self.buffer_metadata['sounds']['mute'] = not self.buffer_metadata['sounds']['mute']

 def announce_buffer_mute (self, first=False):
  if not self.buffer_metadata['sounds']['mute'] and not first:
   output.speak(_("Buffer mute off"), True)
  elif self.buffer_metadata['sounds']['mute']:
   output.speak(_("Buffer mute on"), not first)

 def play(self, *args, **kwargs):
  if 'honor_mute' in kwargs:
   honor_mute = kwargs['honor_mute']
  else:
   honor_mute = True
  if honor_mute and self.buffer_metadata['sounds']['mute']:
   return
  self.session.play(*args, **kwargs)

 def speak(self, *args, **kwargs):
  if 'honor_mute' in kwargs:
   honor_mute = kwargs['honor_mute']
  else:
   honor_mute = True
  if honor_mute and self.buffer_metadata['sounds']['mute']:
   return
  self.session.speak(*args, **kwargs)

 @buffer_defaults
 def speak_item(self, index=None, interrupt=True):
  try:
   formatted = self.format_item(index)
  except IndexError:
   return output.speak(_("No items in %s." % self.name), interrupt)
  output.speak(formatted, interrupt)

 def speak_index(self):
  answer = _("Item %d of %d.") % (len(self) - self.index, len(self))
  output.speak(answer)

 def get_item_metadata(self):
  return self.item_fields

 @buffer_defaults
 def get_item_data(self, index=None, item=None):
  data = dict()
  fields = self.get_item_metadata()
  for (name, field) in fields.iteritems():
   value = field.get_value(index=index, item=item)
   if value is not None:
    data[name] = value
   else:
    logging.debug("The value of {name} is None, excluding from the returned dictionary.".format(name=name))
  return data

 def set_field(self, name, display_name, field, processor=None, field_type=meta.FT_TEXT, filter=True):
  if field is None:
   field = (self, name)
  elif isinstance(field, basestring):
   field = (self, field)
  elif isinstance(field, tuple):
   if any((callable(x) for x in field)):
    base_field = field[0]
    field_stack = field[1:]
    if base_field is None:
     base_field = (self, name)
    elif isinstance(base_field, basestring):
     base_field = (self, base_field)
    elif isinstance(base_field, tuple):
     base_field = (self,) + base_field
    field = (base_field,) + field_stack
   else:
    field = (self,) + field
  self.item_fields[name] = meta.Field(display_name, field, processor=processor, field_type=field_type, filter=filter)
 
 def del_field(self, name):
  del self.item_fields[name]
 
 def clear_fields(self):
  self.item_fields = {}
 
 def get_template(self, name="spoken"):
  if name in self.buffer_metadata:
   return self.buffer_metadata[name]
  else:
   return self.get_default_template(name)

 def get_default_template(self, name="spoken"):
  if name != "spoken" and "spoken" in self.buffer_metadata:
   return self.buffer_metadata['spoken']
  else:
   key = None
   if name == "clipboard" and hasattr(self, "default_clipboard_template"):
    key = self.default_clipboard_template
   elif hasattr(self, "default_template"):
    key = self.default_template
   if key in self.session.config['templates']:
    return self.session.config['templates'][key]
   elif len(self.item_fields) == 1:
    return "$" + self.item_fields.keys()[0]
   else:
    return ""

 @property
 def current_item(self):
  return self[self.index]

 def get_index_matching(self, search_key, search):
  for n, i in enumerate(self):
   if i[search_key] == search:
    return n
  raise ValueError("No item exists with %s set to %r" % (search_key, search))

 @buffer_defaults
 def get_item_field(self, index, field):
  if isinstance(field, basestring): #I later hope to allow for nested fields
   return self[index][field]
