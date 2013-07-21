import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'keymap' in root['config'].keys() and 'viewProfile' in root['config']['keymap'].keys():
   del root['config']['keymap']['viewProfile']
