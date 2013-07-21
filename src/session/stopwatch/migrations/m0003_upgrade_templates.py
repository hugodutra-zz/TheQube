import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'templates' in root['config']:
   root['config']['templates']['timer'] = "$name: $elapsed"
   root['config']['templates']['countdown'] = "$name: $remaining"
