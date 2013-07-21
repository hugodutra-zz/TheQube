import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'buffers' in root['config'] and 'Sent' in root['config']['buffers']:
   if 'sounds' not in root['config']['buffers']['Sent']:
    root['config']['buffers']['Sent']['sounds'] = dict()
   root['config']['buffers']['Sent']['sounds']['mute'] = True
