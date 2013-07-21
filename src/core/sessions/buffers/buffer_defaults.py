import inspect
from functools import update_wrapper

def buffer_defaults(func):
 def indent(code):
  return "\n".join([" " + line for line in code.split("\n")[:-1]]) + "\n"
 
 argspec = inspect.getargspec(func)
 kwargs = argspec.keywords or "kwargs"
 wrapper = "def wrapper" + inspect.formatargspec(argspec.args, argspec.varargs, kwargs, argspec.defaults) + ":\n"
 wrapper += " from core.sessions.buffers.buffers.buffer import Buffer\n"
 wrapper += " import sessions\n"
 if 'buffer' in argspec.args:
  set_buffer = "if buffer is None: buffer = sessions.current_session.current_buffer\n"
 elif argspec.args[0] == "self":
  set_buffer = "if isinstance(self, Buffer): buffer = self\n"
  set_buffer += "elif isinstance({kwargs}.get('buffer', None), Buffer): buffer = {kwargs}['buffer']\n"
  set_buffer += "else: buffer = sessions.current_session.current_buffer\n"
 else:
  set_buffer = "if isinstance({kwargs}.get('buffer', None), Buffer): buffer = {kwargs}['buffer']\n"
  set_buffer += "else: buffer = sessions.current_session.current_buffer\N"
 set_index = set_buffer
 if 'index' in argspec.args:
  set_index += "if index is None: index = buffer.index\n"
 else:
  set_index += "if {kwargs}.get('index', None) is not None: index = {kwargs}['index']\n"
  set_index += "else: index = buffer.index\n"
 if 'item' in argspec.args:
  set_item = "if item is None:\n"
  set_item += indent(set_index)
  set_item += " item = buffer[index] #1\n"
 else:
  set_item = "if {kwargs}.get('item', None) is not None: item = {kwargs}['item']\n"
  set_item += "else:\n"
  set_item += indent(set_index)
  set_item += " item = buffer[index] #2\n"
 if argspec.keywords is not None:
  wrapper += indent(set_item)
  if 'buffer' not in argspec.args:
   if argspec.args[0] == "self":
    wrapper += " if not isinstance(self, Buffer): {kwargs}['buffer'] = buffer\n"
   else:
    wrapper += " {kwargs}['buffer'] = buffer\n"
  elif 'index' not in argspec.args:
   wrapper += " {kwargs}['index'] = index\n"
  elif 'item' not in argspec.args:
   wrapper += " {kwargs}['item'] = item\n"
 elif 'item' in argspec.args:
  wrapper += indent(set_item)
 elif 'index' in argspec.args:
  wrapper += indent(set_index)
 elif 'buffer' in argspec.args:
  wrapper += indent(set_buffer)
 wrapper += " return func" + inspect.formatargspec(argspec.args, argspec.varargs, argspec.keywords) + "\n"
 wrapper += "f = wrapper\n"
 wrapper = wrapper.format(kwargs=kwargs)
 bindings = {'func':func, 'f':None}
 exec wrapper in bindings
 update_wrapper(bindings['f'], func)
 return bindings['f']
