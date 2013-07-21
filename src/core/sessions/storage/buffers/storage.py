from logger import logger
logging = logger.getChild('sessions.buffers.buffers.storage')

from utils.wx_utils import always_call_after

from core.sessions.buffers.buffer_defaults import buffer_defaults

from core.sessions.buffers.buffers.buffer import Buffer

class Storage (Buffer):
 """Buffer class which implements storage on top of the persistent storage session"""

 def __init__ (self, session, name=None, data=[], location=None, *args, **kwargs):
  if not location:
   location = name
  with session.storage_lock:
   self.location = self.SanitizeLocationString(location)
   if self.location not in session.storage.keys():
    session.storage[self.location] = []
   if self.location not in session.buffer_metadata.keys():
    session.buffer_metadata[self.location] = {}
   self.storage = session.storage[self.location]
   self.buffer_metadata = session.buffer_metadata[self.location]
   super(Storage, self).__init__(session=session, name=name, *args, **kwargs)
   self.storage.extend(data)

 def SanitizeLocationString (self, name):
  name = name.replace(' ', '_')
  name = name.replace('/', '_')
  name = name.replace('#', '_')
  name = name.replace('*', '_')
  name=name.replace('"', '_')
  name = name.replace('%', '_')
  return unicode(name)

 def sync (self):
  self.session.sync()

 def clear(self):
  with self.session.storage_lock: super(Storage, self).clear()

 def destroy(self):
  del self.session.buffer_metadata[self.location]
  with self.session.storage_lock: del self.session.storage[self.location]
  self.set_index(0, False)
  super(Storage, self).destroy()

 def get_index (self):
  return int(self.buffer_metadata.get('index', 0))

 def set_index(self, index, undoable=True):
  super(Storage, self).set_index(index, undoable)
  self.buffer_metadata['index'] = self._index

 index = property(fget=get_index, fset=set_index)

 @buffer_defaults
 def remove_item(self, index=None):
  with self.session.storage_lock: super(Storage, self).remove_item(index)

 def shutdown (self, end=False):
  with self.session.storage_lock:
   return super(Storage, self).shutdown(end)
