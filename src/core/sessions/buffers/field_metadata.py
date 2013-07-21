from logger import logger
logging = logger.getChild('core.buffers.field_metadata')

import inspect

FIELD_TYPES = (FT_NUMERIC, FT_TEXT, FT_BOOL) = range(3)

class Field (object):
 
 def __init__(self, display_name, field, processor=None, field_type=FT_TEXT, filter=True):
  if not isinstance(display_name, basestring) or len(display_name) == 0:
   raise ValueError("'display_name' must be a non-empty string.")
  if not isinstance(field, tuple) and not callable(field):
   raise TypeError("'field' must be a tuple.")
  if isinstance(field, tuple) and len(field) < 2 and not callable(field):
   raise ValueError("'field' must have 2 or more items.")
  if field_type not in FIELD_TYPES:
   raise ValueError("Invalid field type value.")
  if not isinstance(filter, bool):
   raise TypeError("The 'filter' argument must be a bool.")
  self.display_name = display_name
  self.field = field
  self.processor = processor
  self.field_type = field_type
  self.filter = filter
  if isinstance(self.field, tuple):
   if isinstance(self.field[0], tuple) or callable(self.field[0]):
    self._stack_fields()
   else:
    self._compile_field()
  supported_args = inspect.getargspec(self.field)[0]
  self.use_index = 'index' in supported_args
  self.use_item = 'item' in supported_args

 def copy(self):
  return Field(self.display_name, self.field, processor=self.processor, field_type=self.field_type, filter=self.filter)

 def get_value(self, index=None, item=None):
  value = None
  try:
   kwargs = {}
   if index is not None and self.use_index:
    kwargs['index'] = index
   if item is not None and self.use_item:
    kwargs['item'] = item
   value = self.field(**kwargs)
  except:
   logging.exception("An exception was raised while trying to get a field's value.")
  #Boolean fields must always have a value.
  if value is None and self.field_type == FT_BOOL:
   value = False
  if callable(self.processor):
   value = self.processor(value)
  return value

 def _compile_field(self):
  from core.sessions.buffers.buffers.buffer import Buffer
  if not isinstance(self.field[0], Buffer):
   raise TypeError("The first item in a field tuple must be a buffer.")
  bindings = {'f':None, 'buffer':self.field[0]}
  field_code = "def field(item):\n"
  keys = self.field[1:]
  if self.field_type == FT_BOOL:
   field_code += " return bool(item.get('{0}', None))\n".format("', {}).get('".join(keys))
  else:
   field_code += " return item.get('{0}', None)\n".format("', {}).get('".join(keys))
  field_code += "f = field"
  exec field_code in bindings
  self.field = bindings['f']

 def _stack_fields(self):
  field_stack = self.field
  if isinstance(field_stack[0], tuple):
   self.field = field_stack[0]
   self._compile_field()
   field_stack = (self.field,) + field_stack[1:]
  argspec = inspect.getargspec(field_stack[0])
  if argspec.args[0] == 'self':
   argspec = argspec._replace(args=argspec.args[1:])
  mapping = {}
  inner = "f0" + inspect.formatargspec(*argspec[:2])
  mapping['f0'] = field_stack[0]
  for i in range(1, len(field_stack)):
   inner = "f{i}({inner})".format(i=i, inner=inner)
   mapping['f' + str(i)] = field_stack[i]
  stack_code = "def stacked_field" + inspect.formatargspec(*argspec) + ":\n"
  stack_code += " return " + inner + "\n"
  stack_code += "f=stacked_field\n"
  mapping['f'] = None
  exec stack_code in mapping
  self.field = mapping['f']
