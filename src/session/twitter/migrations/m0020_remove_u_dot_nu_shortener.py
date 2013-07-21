import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'shortener' in root['config'] and 'urlShortener' in root['config']['shortener'] and root['config']['shortener']['urlShortener'] == 'U.Nu':
   root['config']['shortener']['urlShortener'] = 'Bit.Ly'
