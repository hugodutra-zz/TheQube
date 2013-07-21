from logger import logger
logging = logger.getChild('core.sessions.storage')

from copy import deepcopy

import config
import gc
import paths
import os
import output
import threading
import misc

from core.sessions.session import Session
from storage_migration import Migrator

class Storage (Session):
 syncInterval = 600 #interval for syncing storage to disk.
 syncIdle = 180 #minimum idle time before syncing storage to disk 

 def __init__ (self, name=None, *args, **kwargs):
  #Setup the primary session storage.
  self.database_path = self._determine_database_path(name)
  FileStorage, Connection = misc.import_durus()
  self.store = FileStorage(self.database_path)
  self.connection = Connection(self.store)
  self.storage_lock = threading.RLock()
  logging.debug("%s: Creating primary session storage." % name)
  self.storage = self.connection.get_root()
  self.storage['_updated'] = misc.GetTickCount()
  self.storage['name'] = name
  self.migrate()
  if not hasattr(self, "interval"):
   self.interval = self.syncInterval
  if not hasattr(self, "idle"):
   self.idle = self.syncIdle
  self.timer = None
  self.updater(True)
  super(Storage, self).__init__(name=name, *args, **kwargs)

 def sync(self, forced=False, speak=False):
  current = misc.GetTickCount()
  idle = (current - misc.GetLastInputInfo()) / 1000
  since_last_sync = (current - self.storage['_updated']) / 1000
  logging.debug("Synchronizer: Session %s was last synced %s seconds ago, and system has been idle %s seconds." % (self.name, since_last_sync, idle))
  if not forced and since_last_sync < 3600 and (idle < self.idle or since_last_sync < self.interval):
   return
  logging.info("Synchronizer: Syncing storage for session %s to disk." % self.name)
  with self.storage_lock:
   try:
    if self.storage.has_key('config') and self.storage['config'].has_key('buffers') and hasattr(self, 'buffer_metadata'):
     self.storage['config']['buffers'] = deepcopy(self.buffer_metadata)
    self.connection.get_root()['_updated'] = misc.GetTickCount()
    self.connection.commit()
    self.pack()
    gc.collect()
   except:
    if speak:
     output.speak(_("Sync failed."))
    logging.exception("%s: Synchronizer: Unable to sync session to disk." % self.name)
    return
  if speak:
   output.speak(_("Sync completed."))

 def shutdown (self, delete = False, *args, **kwargs):
  try:
   self.timer.cancel()
   logging.debug("%s: Synchronizer: Deactivated sync storage timer." % self.name)
  except:
   logging.exception("%s: Synchronizer: Error shutting down timer." % self.name)
  self.sync(forced=True)
  self.store.close()
  if delete:
   try:
    os.remove(self.database_path)
   except:
    logging.debug("Unable to delete session data file.")
  super(Storage, self).shutdown(*args, **kwargs)

 def pack(self):
  try:
   self.connection.pack()
  except:
   logging.exception("%s: Unable to pack storage." % self.name)
  try:
    os.remove("%s.prepack" %(self.database_path))
  except:
   #Sometimes the file isn't there, don't touch.
   pass

 def updater (self, first=False):
  self.timer = threading.Timer(60, self.updater)
  self.timer.start()
  try:
   if not first:
    self.sync()
  except:
   logging.exception("Synchronizer: Unable to sync storage for session %s to disk." % self.name)
 
 def migrate(self):
  Migrator(self).migrate()

 def _determine_database_path(self, name):
  return os.path.join(self.session_path, '%s.durus' % name)

"""
 def rename (self, name):
  self.rename_storage_file (name)
  super(Storage, self).rename(name)

 def rename_storage_file (self, name):
  (FileStorage, Connection) = misc.import_durus()
  self.sync(forced=True)
  self.store.close()
  logging.debug("%s: Rename process: Deactivated session storage." % self)
  try:
   os.rename(self.database_path)
   self.store = FileStorage(self.database_path)
   self.connection = Connection(self.store)
   self.storage = self.connection.get_root()
   self.storage['name'] = name
   logging.debug("%s: Storage file successfully renamed and remounted." % self)
  except exception as e:
   raise sessions.RenameError(e)
"""