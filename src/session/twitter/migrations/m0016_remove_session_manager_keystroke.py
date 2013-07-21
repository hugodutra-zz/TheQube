import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'keymap' in root['config'].keys() and 'SessionManager' in root['config']['keymap'].keys():
   del root['config']['keymap']['SessionManager']
  if 'keymap' in config.main.keys() and 'SessionManager' in config.main['keymap'].keys():
   del config.main['keymap']['SessionManager']
   config.main.write()
