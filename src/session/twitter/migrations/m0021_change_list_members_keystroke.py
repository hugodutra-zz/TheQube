import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root and 'keymap' in root['config'] and 'ListMembers' in root['config']['keymap']:
   root['config']['keymap']['ListMembers'] = "alt+win+]"
