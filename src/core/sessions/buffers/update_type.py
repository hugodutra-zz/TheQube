import functools

def set_update_type(func):
 def set_update_type_wrapper (cls, *args, **kwargs):
  if 'update_type' in kwargs and kwargs['update_type'] not in cls._update_types.values():
   kwargs['update_type'] = cls._update_types['default']
  return func(cls, *args, **kwargs)
 functools.update_wrapper(set_update_type_wrapper, func)
 return set_update_type_wrapper
