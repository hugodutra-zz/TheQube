from conditional_template import ConditionalTemplate as Template

(RANGE_ALL, RANGE_ALL_REVERSED, RANGE_CUSTOM) = range(3)
class BaseExporter (object):
 def __init__(self, buffer, filename, item_template=None, first=None, last=None, range_type=RANGE_ALL, **kwargs):
  self.buffer = buffer
  self.first = first
  self.last = last
  self.filename = filename
  if item_template is not None:
   self.item_template = Template(item_template)
  else:
   self.item_template = None
  self.range_type = range_type
  if self.range_type not in (RANGE_ALL, RANGE_ALL_REVERSED, RANGE_CUSTOM):
   raise ValueError("'range_type' is not a valid range type identifier.")
  if self.range_type == RANGE_CUSTOM and (self.first is None or self.last is None):
   raise ValueError("'first' and 'last' are required for a custom range.")
 
 def __enter__(self):
  self.buffer.session.storage_lock.acquire()
  try:
   if self.range_type == RANGE_ALL:
    self.first = 0
    self.last = len(self.buffer) - 1
    self.reversed = False
   elif self.range_type == RANGE_ALL_REVERSED:
    self.first = len(self.buffer) - 1
    self.last = 0
    self.reversed = True
   elif self.range_type == RANGE_CUSTOM:
    if self.first < 0:
     self.first = 0
    elif self.first >= len(self.buffer):
     self.first = len(self.buffer) - 1
    if self.last >= len(self.buffer):
     self.last = len(self.buffer) - 1
    elif self.last < 0:
     self.last = 0
    self.reversed = self.last < self.first
   self.export_total = abs(self.last - self.first) + 1
  except:
   self.buffer.session.storage_lock.release()
   raise
  return self
 
 def __exit__(self, exc_type, exc_value, exc_tb):
  self.buffer.session.storage_lock.release()
  return False
 
 def GetItems(self):
  export_index = 1
  if self.reversed:
   item_indices = xrange(self.first, self.last - 1, -1)
  else:
   item_indices = xrange(self.first, self.last + 1, 1)
  for i in item_indices:
   mapping = self.buffer.get_item_data(i)
   mapping['total'] = self.export_total
   mapping['index'] = export_index
   (yield mapping)
   export_index += 1

 def GetFormattedItems(self):
  if self.item_template is None:
   raise NotImplementedError
  for item in self.GetItems():
   (yield self.item_template.Substitute(item))

 def Run(self):
  raise NotImplementedError

 @classmethod
 def GetSupportedArgs(self):
  return ['buffer', 'filename', 'item_template', 'range']

 @classmethod
 def GetFileExtension(self):
  raise NotImplementedError
 
 @classmethod
 def GetName(self):
  raise NotImplementedError
