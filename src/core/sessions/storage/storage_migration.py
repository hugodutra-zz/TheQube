"""
Classes and utility methods to aid in migrating the storage structure.
"""
from logger import logger
logging = logger.getChild('core.sessions.storage_migration')

import sys, os
from datetime import datetime

class MigrationBase (object):
 def __init__(self, session):
  self.session = session
 
 def forwards(self):
  raise NotImplementedError
 
 def backwards(self):
  raise NotImplementedError

class Migrator(object):
 """
 The migrator takes a session and knows how to migrate it.
 The current implementation is durus specific and assumes the session
 is a descendent of the storage based session.
 """
 
 def __init__ (self, session):
  self.session = session
  self.connection = session.connection
  with session.storage_lock:
   try:
    session.connection.get_root()['migrations']
   except KeyError:
    session.connection.get_root()['migrations'] = {}
    session.connection.commit()
   self._applied_migrations = self.connection.get_root()['migrations'].keys()
 
 def migrate (self):
  """
  Migrate to the latest migration that's available.
  
  TODO: rollbacks/backwards migrating?
  """
  migrations = self._list_migrations()
  new_migrations = sorted([m for m in migrations if not m in self._applied_migrations])
  for migration in new_migrations:
   self._run_migration(migration, direction="forwards")
  
 # Private methods  used by migrate
 
 def _list_migrations (self):
  """Returns a sorted list of all migrations available for the current session."""
  migrations = []
  try:
   mod = self._get_migrations_module()
  except ImportError:
   # No migrations module for this session
   return []
  # Sort and filter duplicates by putting the migrations in a set
  return set(mod.__all__)
 
 def _run_migration(self, migration_id, direction="forwards"):
  """
  Run the specified migration in the specified direction.
  Makes sure the migration is embedded in a transaction.
  """
  mod = self._get_migrations_module().__name__+"."+migration_id
  __import__(mod)
  mod = sys.modules[mod]
  migration_class = getattr(mod, 'Migration')
  migration_instance = migration_class(self.session)
  try:
   getattr(migration_instance, direction)
  except AttributeError:
   logging.warning('Function %s not found in migration class' % direction)
   raise
  with self.session.storage_lock:
   try:
    getattr(migration_instance, direction)()
    self.connection.commit()
   except:
    self.connection.abort()
    logging.warning('Something went wrong running the migration, transaction aborted')
    raise
   self.connection.get_root()['migrations'][migration_id] = {'timestamp': datetime.now(), 'direction': direction}
   self.connection.commit()

 def _get_migrations_module(self):
  def get_module(mod):
   try:
    return sys.modules[mod]
   except KeyError:
    __import__(mod)
    return sys.modules[mod]
  
  session_module = get_module (self.session.__module__)
  migrations_module_name = session_module.__package__+".migrations"
  migrations_module = get_module(migrations_module_name)
  return migrations_module