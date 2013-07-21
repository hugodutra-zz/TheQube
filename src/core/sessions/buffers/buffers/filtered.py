from logger import logger
logging = logger.getChild('core.buffers.filtered')

from pydispatch import dispatcher

import inspect
from itertools import chain
import output
import signals

from core.sessions.buffers.buffer_defaults import buffer_defaults

from dismissable import Dismissable
from core.sessions.storage.buffers.storage import Storage
from conditional_template import ConditionalTemplate as Template
import re

from core.sessions.buffers import field_metadata as meta

class Filtered (Dismissable, Storage):

 def __init__ (self, term="", remove=False, source_name="", data=[], fields=[], useRegex=False, *args, **kwargs):
  self.item_fields = {}
  super(Filtered, self).__init__(*args, **kwargs)
  self.store_args({'term':term, 'remove':remove, 'source_name':source_name, 'fields':fields, 'useRegex':useRegex})
  source = self.session.get_buffer_by_name(source_name)
  if not source:
   return logging.warn("%s: Could not locate source buffer %r" % (self.session, source_name))
  if not data and not self:
   #Experimental code - if works, need to make more elegant!
   data = source
  self.set_flag('configurable', False)
  self.set_flag('filterable', True)
  self.set_flag('clearable', True)
  self.set_flag('export', source.get_flag('export'))
  self.set_flag('updatable', source.get_flag('updatable'))
  self.term = term
  self.remove = remove
  self.source = source
  self.fields = fields
  self.useRegex = useRegex
  if self.useRegex:
   self.regex = re.compile(self.term, re.IGNORECASE | re.DOTALL | re.UNICODE)
  else:
   self.term = self.term.lower()
  if isinstance(self.source, Filtered):
   self.master = self.source.master
   #dispatcher.connect(self.extend, signals.buffer_updated, self.master)
  else:
   self.master = self.source
  metadata = self.source.get_item_metadata()
  self.cached_getters = []
  for field_name in metadata.iterkeys():
   if field_name in ('source_index', 'source_total', 'master_index', 'master_total'):
    continue
   field = metadata[field_name].copy()
   if field.use_index and not field.use_item:
    field.field = self._CallSourceFunction(field.field)
   if field_name == "index":
    #field.display_name = _("Source Index")
    #self.item_fields['source_index'] = field
    pass   
   elif field_name == "total":
    #field.display_name = _("Source Total")
    #self.item_fields['source_total'] = field
    pass
   else:
    self.item_fields[field_name] = field
   if field_name in self.fields or (len(self.fields) < 1 and field.filter and field.field_type == meta.FT_TEXT):
    self.cached_getters.append(field.get_value)
  #self.set_field('master_index', _("Master Index"), (lambda index: len(self.master) - self.master.index_of(self[index])), field_type=meta.FT_NUMERIC, filter=False)
  #self.set_field('master_total', _("Master Total"), (lambda index: len(self.master)), field_type=meta.FT_NUMERIC, filter=False)
  self.cached_getters = tuple(self.cached_getters)
  dispatcher.connect(self.remove_self, signals.dismiss_buffer, source)
  dispatcher.connect(self.remove_source_item, signals.remove_item, source)
  if hasattr(self, "clear"):
   dispatcher.connect(self.clear, signals.clear_buffer, source)
  dispatcher.connect(self.extend, signals.buffer_updated, source)
  if not self:
   super(Filtered, self).clear()
   self.extend(data)

 def __getattr__(self, name):
  if name != "source" and getattr(self, "source", None):
   member = getattr(self.source, name)
   if callable(member):
    return self._CallSourceFunction(member)
   else:
    return member

 def _CallSourceFunction(self, func):
  def modifier(*args, **kwargs): 
   argspec = inspect.getargspec(func)
   if kwargs.get("index") is not None:
    index = kwargs["index"]
    if not (index == 0 and len(self) == 0):
     kwargs["index"] = self.source.index_of(self[index])
   elif "index" in argspec.args:
    args = list(args)
    if not args:
     args.append(None)
    index = args[0]
    if not index and index != 0:
     index = self.index
    if not (index == 0 and len(self) == 0):
     args[0] = self.source.index_of(self[index])
   return func(*args, **kwargs)
  return modifier

 def extend(self, items, *args, **kwargs):
  answer = []
  for item in items:
   if self.item_matches(item) and not super(Filtered, self).item_exists(item):
    answer.append(item)
  dispatcher.send(sender=self, signal=signals.buffer_updated, items=answer)
  return super(Filtered, self).extend(answer)

 def item_matches(self, item):
  for getter in self.cached_getters:
   field = getter(item=item)
   if field is None:
    continue
   else:
    field = unicode(field)
   if self.useRegex:
    result = self.regex.search(field) is not None
   else:
    result = field.lower().find(self.term) != -1
   if result:
    return not self.remove
  return self.remove

 def remove_source_item(self, item):
  try:
   super(Filtered, self).remove_item(self.index_of(item))
  except:
   pass
  if self.index == len(self):
   self.set_index(self.index-1, False)
  dispatcher.send(sender=self, signal=signals.remove_item, item=item)

 @buffer_defaults
 def remove_item(self, index=None):
  self.source.remove_item(self.source.index_of(self[index]))

 def get_template(self, name="spoken"):
  return self.master.get_template(name)

 def remove_self (self):
  if hasattr(self.session, "remove_buffer"):  
   self.session.remove_buffer(self)

 def clear (self):
  logging.debug("Removing filtered tweets from source.")
  for counter, i in enumerate(self):
   self.source.remove_item(index=self[counter])
  message = _("Removed all matching items from source %s") % self.source
  self.source.index -= len(self)
  output.speak(message, True)
  super(Filtered, self).clear()

 def shutdown(self, *args, **kwargs):
  logging.debug("%s: Disconnecting filter %s from all source signals." % (self.session, self))
  try:
   dispatcher.disconnect(self.remove_self, signals.dismiss_buffer, self.source)
   dispatcher.disconnect(self.remove_source_item, signals.remove_item, self.source)
   if hasattr(self, "clear"):
    dispatcher.disconnect(self.clear, signals.clear_buffer, self.source)
   dispatcher.disconnect(self.extend, signals.buffer_updated, self.source)
  except:
   logging.exception("%s: There was an error disconnecting filter %s from source signals." % (self.session, self))
  return super(Filtered, self).shutdown(*args, **kwargs)

 def update(self, *args, **kwargs):
  return self.master.update(*args, **kwargs)

 def retrieve_update(self, *args, **kwargs):
  return self.master.retrieve_update(*args, **kwargs)

 @staticmethod
 def generate_filter_name(source, filter_spec):
  inclusions = []
  exclusions = []
  term = filter_spec.get('term', "")
  remove = filter_spec.get('remove', False)
  useRegex = filter_spec.get('useRegex', False)
  walker = source
  while walker is not None:
   if useRegex:
    term = _("rx {term}").format(term=term)
   if remove:
    exclusions.append(term)
   else:
    inclusions.append(term)
   if isinstance(walker, Filtered):
    term = getattr(walker, 'term', "")
    remove = getattr(walker, 'remove', False)
    useRegex = getattr(walker, 'useRegex', False)
    walker = walker.source
   else:
    base_name = walker.name
    walker = None
  inclusions.reverse()
  exclusions.reverse()
  if len(inclusions) == 1:
   with_terms = inclusions[0]
  elif len(inclusions) == 2:
   with_terms = _(" and ").join(inclusions)
  elif len(inclusions) > 2:
   with_terms = _(", ").join(inclusions[0:-1])
   with_terms = _(", and ").join((with_terms, inclusions[-1]))
  if len(exclusions) == 1:
   without_terms = exclusions[0]
  elif len(exclusions) == 2:
   without_terms = _(" or ").join(exclusions)
  elif len(exclusions) > 2:
   without_terms = _(", ").join(exclusions[0:-1])
   without_terms = _(", or ").join((without_terms, exclusions[-1]))
  if len(inclusions) > 0 and len(exclusions) == 0:
   name = _("{0} with {1}").format(base_name, with_terms)
  elif len(exclusions) > 0 and len(inclusions) == 0:
   name = _("{0} without {1}").format(base_name, without_terms)
  elif len(inclusions) == 1 and len(exclusions) == 1:
   name = _("{0} with {1} and without {2}").format(base_name, with_terms, without_terms)
  else:
   name = _("{0} with {1}. Without {2}").format(base_name, with_terms, without_terms)
  return name
