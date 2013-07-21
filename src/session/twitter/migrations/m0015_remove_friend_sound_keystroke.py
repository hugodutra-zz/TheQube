import config
from core.sessions.storage.storage_migration import MigrationBase

class Migration (MigrationBase):
 def forwards(self):
  root = self.session.connection.get_root()
  if 'config' in root.keys() and 'keymap' in root['config'].keys() and 'FriendSound' in root['config']['keymap'].keys():
   del root['config']['keymap']['FriendSound']
  if 'keymap' in config.main.keys() and 'FriendSound' in config.main['keymap'].keys():
   del config.main['keymap']['FriendSound']
   config.main.write()
