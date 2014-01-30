
from core.sessions.buffers.buffers import Buffer

class APICount (Buffer):
 """Abstract class to provide the machinery for buffers that have a max API calls to use setting."""

 def __init__ (self, session, count=None, maxAPIPerUpdate=None, *args, **kwargs):
  self.maxAPIPerUpdate = maxAPIPerUpdate or self.buffer_metadata.get('maxAPIPerUpdate', session.config['updates']['maxAPIPerUpdate'])
  self.count = count or self.buffer_metadata.get('retrieveCount', session.config['counts']['retrieveCount'])
  if 'retrieveCount' not in self.buffer_metadata.keys():
   self.buffer_metadata['retrieveCount'] = self.count
  if 'maxAPIPerUpdate' not in self.buffer_metadata.keys():
   self.buffer_metadata['maxAPIPerUpdate'] = self.maxAPIPerUpdate
  self.maxAPIPerUpdate = self.buffer_metadata['maxAPIPerUpdate']
  self.count = self.buffer_metadata['retrieveCount']
  self.store_args({'maxAPIPerUpdate':maxAPIPerUpdate, 'count':count})
  super(APICount, self).__init__ (session, *args, **kwargs)

 def paged_update (self, update_function_name, MaxID_arg='max_id', count_arg='count', respect_count=True, *args, **kwargs):
  id = None
  results = []
  if respect_count:
   kwargs[count_arg] = self.count
  i = 0
  while i < self.maxAPIPerUpdate:
   i += 1
   kwargs[MaxID_arg] = id
   new_data = self.session.api_call(update_function_name, report_success=False, report_failure=False, *args, **kwargs)
   if type(new_data) == tuple:
    new_data = new_data[0]
   if not new_data:
    break
   id = new_data[-1]['id'] -1
   results.append(new_data)
  return self.merge_segments(results)

 def cursored_update (self, update_function_name, cursor_arg='cursor', count_arg='count', respect_count=True, *args, **kwargs):
  next_cursor = -1
  results = []
  if respect_count:
   kwargs[count_arg] = self.count
  i = 0
  while next_cursor and i < self.maxAPIPerUpdate:
   i += 1
   kwargs[cursor_arg] = next_cursor
   new_data = self.session.api_call(update_function_name, report_success=False, report_failure=False, *args, **kwargs)
   if type(new_data) == tuple:
    new_data = new_data[0]
   next_cursor = new_data['next_cursor']
   results.append(new_data)
  return self.merge_segments(results)

 @staticmethod
 def merge_segments (lst):
  #Makes a couple ugly assumptions, the worst being that all supplied items in the packed list are the same length.
  def merge_dicts (num):
   res = dict(lst[num])
   for (n, d) in enumerate(lst):
    if n != num:
     for k in d:
      if type(d[k]) == list:
       res[k].extend(d[k])
      else:
       #It's not a list, why not make it into one?
       if type(res[k]) != list:
        res[k] = [res[k]]
       res[k].append(d[k])
   return res
  def merge_lists (num):
   res = list(lst[num])
   for (n, l) in enumerate(lst):
    if n != num and type(l) == list:
     res.extend(l)
    elif n != num and type(l) != list:
     res.append(l)
   return res
  for (num, item) in enumerate(lst):
   if hasattr(item, 'keys'): #So how else am I supposed to check for a dict?
    return merge_dicts(num)
   elif type(item) == list: #yuck^2
    return merge_lists(num)
  #we can't do anything with it
  return lst
